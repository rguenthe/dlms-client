import os
import sys
import logging
import time
import datetime
import shutil

import dlmclient.system as system
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.threads import CmdThread
from dlmclient.scheduler import TaskScheduler
from dlmclient.system.interfaces import wait_for_ip

logger = logging.getLogger('dlmclient')

class Dlmclient(object):
    """
    Datalogger management client: 
    Uploads status reports, downloads configurations and system updates from the DLM server.
    Controls the worker application that does the actual data logging and uploads the recorded data to the DLM server.

    Argument: configfile -- path to the configuration file
    """

    def __init__(self, configfile='/etc/dlmclient.conf'):
        """Initialize Dlmclient instance"""
        self.logger = logging.getLogger('dlmclient')
        self.config = Config(configfile)
        self.scheduler = TaskScheduler()
        self.wwan = None
        self.vpn = None
        self.vpn_iface = None
        self.wwan_connect_timeout = 10
        self.vpn_connect_timeout = 30
        self.server_connect_retry_interval = 120
        self.server_connection_duration = 300
        self.server_connected = False
        self.worker = None

    def configure(self):
        """Configure the DLM client using the given config file."""
        self.wwan = system.interfaces.WwanInterface(iface=self.config.get('wwan', 'iface'))
        self.wwan.configure(apn=self.config.get('wwan', 'apn'), 
                            pin=self.config.get('wwan', 'pin'))
        self.vpn = system.service.SystemService(service=self.config.get('vpn', 'service'))
        self.vpn_iface = self.config.get('vpn', 'iface')

    def schedule_tasks(self):
        """schedule tasks as specified in the config file."""
        status_schedule = self.config.get('config', 'status_upload_schedule').replace(' ','').split(',')
        config_schedule = self.config.get('config', 'config_download_schedule').replace(' ','').split(',')

        status_events = self.scheduler.enter_day_multiple(schedule=status_schedule, prio=2, func=self.upload_status)
        config_events = self.scheduler.enter_day_multiple(schedule=config_schedule, prio=2, func=self.download_config)

        return status_events,config_events

    def start_worker(self):
        """Starts the worker application thread."""
        self.worker = CmdThread(cmd=self.config.get('config', 'worker_exec_path'))
        self.worker.start()

    def upload_status(self):
        """upload a status file to the dlm server."""
        url = self.config.get('config', 'status_upload_url')
        status_file = 'status_%s.xml' %(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        status = Status(self.config)
        status.write_xml(status_file)

        if not self.server_connected:
            ret = self.connect_server()
            if ret is not 0:
                return 1

        ret = system.http.post(url=url, file=status_file)
        if ret is not '200':
            return 1

        shutil.copy(status_file, 'status_files/' + status_file)

        logger.info('status upload successful')
        return 0

    def upload_dataset(self):
        """upload a dataset to the dlm server"""
        url = self.config.get('config', 'data_upload_url')
        output_dir = self.config.get('config', 'worker_output_dir/dataset.xml')

        if not self.server_connected:
            ret = self.connect_server()
            if ret is not 0:
                return 1

        ret = system.http.post(url=url, file=output_dir+'/dataset.xml')
        if ret is not '200':
            return 1

        logger.info('data upload successful')
        return 0

    def download_config(self):
        """download a configuration file from the dlm server"""
        url = self.config.get('config', 'config_download_url')
        url = url + '/' + self.config.get('config', 'serial')
        config_file = 'server_config_%s.xml' %(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
        
        if not self.server_connected:
            ret = self.connect_server()
            if ret is not 0:
                return 1

        ret = system.http.get(url=url, dest_file=config_file)
        if ret is not '200':
            return 1

        ret = self.config.read_xml(config_file)
        if ret is not 0:
            logger.error('could not read downloaded config file')
            return 1

        shutil.copy(config_file, 'config_files/' + config_file)

        logger.info('config update from server successful')
        return 0

    def connect_server(self, max_attempts=3):
        """Initiates a connection to the DLM Server."""
        attempts = 0

        # retry to establish connection
        while attempts < max_attempts:
            print("Attempt server connection ...")
            self.wwan.up()
            wwan_ip = wait_for_ip(self.wwan.iface, timeout=self.wwan_connect_timeout)
            if wwan_ip is None:
                logger.error('could not connect wwan interface')
                self.disconnect_server(wwan=wwan, vpn=vpn)
                time.sleep(server_connect_retry_interval)
                attempts = attempts + 1
                continue

            vpn.ctrl('start')
            vpn_ip = wait_for_ip(vpn_iface, timeout=self.vpn_connect_timeout)
            if Vpn_ip is None:
                logger.error('could not connect to vpn service')
                self.disconnect_server(wwan=wwan, vpn=vpn)
                attempts = attempts + 1
                time.sleep(server_connect_retry_interval)
                continue
        
        if attempts >= max_attempts:
            logger.error('could not connect to server after %s attempts' %(max_attempts))
            self.wwan.down()
            vpn.ctrl('stop')
            self.server_connected = False
            return 1

        print('Connection to server established')
        logger.info('Connection to server established')
        self.server_connected = True

        # schedule a disconnect from server
        self.scheduler.enter(self.server_connection_duration, 10, self.disconnect_server)

        return (ret, wwan, vpn)

    def disconnect_server(self):
        """Disconnects from the DLM server."""
        self.vpn.ctrl('stop')
        self.iface.down()

        if self.server_connected:
            self.server_connected = False

        logger.info('Disconnected from server')
        return 0
