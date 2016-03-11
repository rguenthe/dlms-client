import os
import logging
import time
import shutil

import dlmclient.system as system
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
        self.events_status_upload = None
        self.events_config_download = None
        self.events_data_upload = None

    def configure_network(self):
        iface = self.config.get('network', 'iface')
        wwan_apn = self.config.get('network', 'wwan_apn')
        wwan_pin = self.config.get('network', 'wwan_pin')
        vpn_iface = self.config.get('network', 'vpn_iface')
        vpn_service = self.config.get('network', 'vpn_service')
        self.vpn_network = OpenvpnNetwork(iface, vpn_iface, vpn_service, wwan=True, wwan_apn=wwan_apn, wwan_pin=wwan_pin)
        log.info('configuring network')

    def schedule_events(self):
        status_schedule = self.config.get('dlmconfig', 'status_upload_schedule').replace(' ', '').split(',')
        config_schedule = self.config.get('dlmconfig', 'config_download_schedule').replace(' ', '').split(',')
        self.events_status_upload = self.scheduler.enter_day_multiple(schedule=status_schedule, prio=1, func=self.upload_status)
        self.events_config_download = self.scheduler.enter_day_multiple(schedule=config_schedule, prio=1, func=self.download_config)
        log.info('scheduling tasks')

    def start_worker(self):
        """Starts the worker application thread."""
        worker_cmd = self.config.get('dlmconfig', 'worker_exec_path')
        self.worker = CmdThread(worker_cmd)
        self.worker.start()
        log.info('started worker')

    def upload_status(self):
        """upload a status file to the dlm server."""
        url = self.config.get('dlmconfig', 'status_upload_url')
        status_file_dir = self.config.get('dirs', 'status_files')

        status_file = 'status_%s.json' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        status = Status(self.config)
        status.write_json(status_file)

        if not self.vpn_network.connected:
            if self.vpn_network.connect() is 0:
                # schedule a network disconnect
                self.scheduler.enter(self.vpn_network.max_connection_duration, 5, self.vpn_network.disconnect)
            else:
                log.error('could not connect to the vpn network')
                return 1

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
        output_dir = self.config.get('dlmconfig', 'worker_output_dir')

        if not self.vpn_network.connected:
            if self.vpn_network.connect() is 0:
                # schedule a network disconnect
                self.scheduler.enter(self.vpn_network.max_connection_duration, 5, self.vpn_network.disconnect)
            else:
                log.error('could not connect to the vpn network')
                return 1

        for file in system.dir.list_files(output_dir):
            if system.http.post(url=url, file=file) is '200':
                shutil.copy(file, data_file_dir + '/' + file)
                os.remove(file)
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

        config_file = 'server_config_%s.xml' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))

        if not self.vpn_network.connected:
            if self.vpn_network.connect() is 0:
                # schedule a network disconnect
                self.scheduler.enter(self.vpn_network.max_connection_duration, 5, self.vpn_network.disconnect)
            else:
                log.error('could not connect to the vpn network')
                return 1

        if system.http.get(url=url, dest_file=config_file) is '200':
            ret = self.config.update_dlmconfig(config_file)
            shutil.copy(config_file, config_file_dir + '/' + config_file)
        else:
            return 1

        log.info('config update from server successful')
        return 0
