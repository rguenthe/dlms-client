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

logger = logging.getLogger('dlmclient')


class Dlmclient(object):
    """
    Datalogger management client: 
    Uploads status reports, downloads configurations and system updates from the DLM server.
    Controls the worker application that does the actual data logging and uploads the recorded data to the DLM server.

    Argument: configfile -- path to the configuration file
    """

    def __init__(self, configfile='/etc/dlmclient.json'):
        """Initialize Dlmclient instance"""
        self.logger = logging.getLogger('dlmclient')
        self.config = Config(configfile)
        self.scheduler = TaskScheduler()
        self.vpnnetwork = OpenvpnNetwork(self.config)
        self.worker = None

    def schedule_tasks(self):
        """schedule tasks as specified in the config file."""
        status_schedule = self.config.get('dlmconfig', 'status_upload_schedule').replace(' ', '').split(',')
        config_schedule = self.config.get('dlmconfig', 'config_download_schedule').replace(' ', '').split(',')

        status_events = self.scheduler.enter_day_multiple(schedule=status_schedule, prio=1, func=self.upload_status)
        config_events = self.scheduler.enter_day_multiple(schedule=config_schedule, prio=1, func=self.download_config)

        return status_events, config_events

    def start_worker(self):
        """Starts the worker application thread."""
        self.worker = CmdThread(cmd=self.config.get('dlmconfig', 'worker_exec_path'))
        self.worker.start()

    def upload_status(self):
        """upload a status file to the dlm server."""
        url = self.config.get('dlmconfig', 'status_upload_url')
        status_file_dir = self.config.get('dirs', 'status_files')

        status_file = 'status_%s.json' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        status = Status(self.config)
        status.write_json(status_file)

        if not self.vpnnetwork.connected:
            ret = self.vpnnetwork.connect()
            if ret is not 0:
                return 1

        ret = system.http.post(url=url, file=status_file)
        if ret is not '200':
            return 1

        shutil.copy(status_file, status_file_dir + '/' + status_file)
        os.remove(status_file)

        # schedule a network disconnect
        self.scheduler.enter(self.vpnnetwork.max_connection_duration, 5, self.vpnnetwork.disconnect)

        logger.info('status upload successful')
        return 0

    def upload_dataset(self):
        """upload a dataset to the dlm server"""
        url = self.config.get('dlmconfig', 'data_upload_url')
        data_file_dir = self.config.get('dirs', 'data_files')
        output_dir = self.config.get('dlmconfig', 'worker_output_dir/dataset.xml')

        if not self.vpnnetwork.connected:
            ret = self.vpnnetwork.connect()
            if ret is not 0:
                return 1

        ret = system.http.post(url=url, file=output_dir + '/dataset.xml')
        if ret is not '200':
            return 1

        # schedule a network disconnect
        self.scheduler.enter(self.vpnnetwork.max_connection_duration, 5, self.vpnnetwork.disconnect)

        logger.info('data upload successful')
        return 0

    def download_config(self):
        """download a configuration file from the dlm server"""
        url = self.config.get('dlmconfig', 'config_download_url')
        url = url + '/' + self.config.get('dlmconfig', 'serial')
        config_file_dir = self.config.get('dirs', 'config_files')

        config_file = 'server_config_%s.xml' % (time.strftime('%Y%m%d_%H%M%S', time.localtime()))

        if not self.vpnnetwork.connected:
            ret = self.vpnnetwork.connect()
            if ret is not 0:
                return 1

        ret = system.http.get(url=url, dest_file=config_file)
        if ret is not '200':
            return 1

        ret = self.config.read_xml(config_file)
        if ret is not 0:
            logger.error('could not read downloaded config file')
            return 1

        self.config.update()
        shutil.copy(config_file, config_file_dir + '/' + config_file)

        # schedule a network disconnect
        self.scheduler.enter(self.vpnnetwork.max_connection_duration, 5, self.vpnnetwork.disconnect)

        logger.info('config update from server successful')
        return 0
