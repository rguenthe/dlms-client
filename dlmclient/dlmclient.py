import os
import logging
import time
import shutil

import dlmclient.system as system
import dlmclient.system.packagemanager as pkg
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.threads import CmdThread
from dlmclient.scheduler import TaskScheduler
from dlmclient.network import OpenvpnNetwork

log = logging.getLogger('dlmclient')


class Dlmclient(object):
    """
    Datalogger management client object:
    Uploads status reports, downloads configurations and system updates from the DLM server.
    Controls the worker application that does the actual data logging and uploads the recorded data to the DLM server.

    Argument: configfile -- path to the configuration file
    """

    def __init__(self, configfile):
        """Initialize Dlmclient instance"""
        self.config = Config(configfile)
        self.scheduler = TaskScheduler()
        self.vpn_network = None
        self.worker = None
        self.postprocessor = None

    def configure_network(self):
        """configure the network connection used to contact the server"""
        iface = self.config.get('network', 'iface')
        wwan_apn = self.config.get('network', 'wwan_apn')
        wwan_pin = self.config.get('network', 'wwan_pin')
        vpn_iface = self.config.get('network', 'vpn_iface')
        vpn_service = self.config.get('network', 'vpn_service')
        self.vpn_network = OpenvpnNetwork(iface, vpn_iface, vpn_service, wwan=True, wwan_apn=wwan_apn, wwan_pin=wwan_pin)
        log.info('configuring network')

    def schedule_events(self):
        """Schedule all tasks for the day as specified in the config"""

        status_schedule = self.config.get('dlmconfig', 'status_upload_schedule').replace(' ', '').split(',')
        self.scheduler.enter_schedule(  schedule=status_schedule,
                                        prio=1,
                                        func=self.upload_status,
                                        pre=self.vpn_network.connect,
                                        post=self.vpn_network.disconnect)

        config_schedule = self.config.get('dlmconfig', 'config_download_schedule').replace(' ', '').split(',')
        self.scheduler.enter_schedule(  schedule=config_schedule,
                                        prio=1,
                                        func=self.download_config,
                                        pre=self.vpn_network.connect,
                                        post=self.vpn_network.disconnect)

        config_schedule = self.config.get('dlmconfig', 'pkg_maintenance_schedule').replace(' ', '').split(',')
        self.scheduler.enter_schedule(  schedule=config_schedule,
                                        prio=1,
                                        func=self.package_maintenance,
                                        pre=self.vpn_network.connect,
                                        post=self.vpn_network.disconnect)

        maintenance_connect_schedule = self.config.get('dlmconfig', 'maintenance_connect_schedule').replace(' ', '').split(',')
        self.scheduler.enter_schedule(  schedule=maintenance_connect_schedule,
                                        prio=1,
                                        func=self.vpn_network.connect)

        maintenance_disconnect_schedule = self.config.get('dlmconfig', 'maintenance_disconnect_schedule').replace(' ', '').split(',')
        self.scheduler.enter_schedule(  schedule=maintenance_disconnect_schedule,
                                        prio=1,
                                        func=self.vpn_network.disconnect)

        log.info('Task scheduling done')

    def worker_start(self):
        """Starts the worker application thread."""
        worker_cmd = self.config.get('dlmconfig', 'worker_exec')
        worker_output = self.config.get('dlmconfig', 'worker_output_path')

        if not os.path.exists(worker_output):
            os.makedirs(worker_output)

        self.worker = CmdThread(worker_cmd)
        self.worker.start()
        log.info('started worker')

    def postprocessor_start(self):
        """Start postprocessing of the generated data"""
        postproc_exec = self.config.get('dlmconfig', 'postprocessing_exec')
        worker_output = self.config.get('dlmconfig', 'worker_output_path')
        postproc_output = self.config.get('dlmconfig', 'postprocessing_output_path')
        postproc_format = self.config.get('dlmconfig', 'postprocessing_output_format')

        if not os.path.exists(postproc_output):
            os.makedirs(postproc_output)

        # cmd: postproc input output json
        postprocessor_cmd = '%s %s %s %s' %(postproc_exec, worker_output, postproc_output, postproc_format)

        self.postprocessor = CmdThread(postprocessor_cmd)
        self.postprocessor.start()

        log.info('postprocessing started with command %s' %postprocessor_cmd)

    def upload_status(self):
        """upload a status file to the dlm server."""
        url = self.config.get('dlmconfig', 'status_upload_url')
        status_file_dir = self.config.get('dirs', 'status_files')

        status_file = 'status_%s.json' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        status = Status(self.config)
        status.write_json(status_file)

        if system.http.post(url=url, file=status_file) is '200':
            shutil.copy(status_file, status_file_dir + '/' + status_file)
            os.remove(status_file)
            ret = 0
        else:
            ret = 1

        log.info('status upload successful')
        return ret

    def upload_dataset(self):
        """upload a dataset to the dlm server"""
        url = self.config.get('dlmconfig', 'data_upload_url')
        data_file_dir = self.config.get('dirs', 'data_files')
        postproc_output = self.config.get('dlmconfig', 'postprocessing_output_path')
        ret = 1

        for file in system.dir.list_files(postproc_output):
            if system.http.post(url=url, file=file) is '200':
                shutil.copy(file, data_file_dir + '/' + file)
                os.remove(file)
                ret = 0
            else:
                log.error('error while uploading dataset files')
                break
                ret = 1

        log.info('data upload successful')
        return ret

    def download_config(self):
        """download a configuration file from the dlm server"""
        url = self.config.get('dlmconfig', 'config_download_url')
        url = url + '/' + self.config.get('dlmconfig', 'serial')
        config_file_dir = self.config.get('dirs', 'config_files')

        config_file = 'server_config_%s.json' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))

        if system.http.get(url=url, dest_file=config_file) is '200':
            ret = self.config.update_dlmconfig(config_file)
            if ret is not 0:
                log.error('could not update config from config file %s' %(config_file))
                return 1
            shutil.copy(config_file, config_file_dir + '/' + config_file)
        else:
            return 1

        log.info('config update from server successful')
        return 0

    def package_maintenance(self):
        """keep packages up to date that are specified in the config."""
        packages = self.config.get('pkgmaintenance', 'upgrade').replace(' ', '').split(',')

        pkg.run_maintenance(packages)

        log.info('package maintenance successful')
        return 0