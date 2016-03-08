import os
import sys
import logging
import time
import datetime

import dlmclient.system as system
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.threads import CmdThread
from dlmclient.scheduler import TaskScheduler

logger = logging.getLogger('dlmclient')

class Dlmclient(object):
    """
    Datalogger management client: 
    Uploads status reports, downloads configurations and system updates from the DLM server.
    Controls the worker application that does the actual data logging and uploads the recorded data to the DLM server.

    Argument: configfile -- path to the configuration file
    """

    def __init__(self, configfile='/etc/dlmclient.conf'):
        """Initialize Dlmclient instance using the given configuration file."""
        self.logger = logging.getLogger('dlmclient')
        self.config = Config(configfile)
        self.scheduler = TaskScheduler()
        self.worker = None
        self.server_connected = False

    def schedule_tasks(self):
        """schedule tasks as specified in the config file."""
        status_schedule = self.config.get('config', 'status_upload_schedule').replace(' ','').split(',')
        status_events = self.scheduler.enter_day_multiple(status_schedule, self.upload_status)

        config_schedule = self.config.get('config', 'config_download_schedule').replace(' ','').split(',')
        config_events = self.scheduler.enter_day_multiple(config_schedule, self.download_config)

        return status_events,config_events

    def start_worker(self):
        """Starts the worker application thread."""
        self.worker = CmdThread(self.config.get('config', 'worker_exec_path'))
        self.worker.start()

    def connect_server(self, max_attempts=3):
        """Initiates a connection to the DLM Server."""
        attempts = 0
        wwan = WwanInterface(self.config.get('wwan', 'iface'))
        wwan.configure(apn=self.config.get('wwan', 'apn'), 
                       pin=self.config.get('wwan', 'pin'))
        vpn = SystemService(self.config.get('vpn', 'service'))
        vpn_iface = self.config.get('vpn', 'iface')

        # retry to establish connection
        while attempts < max_attempts:
            print("Attempt server connection ...")
            wwan.up()
            wwan_ip = wait_for_ip(wwan.iface, timeout=10)
            if wwan_ip is None:
                logger.error('could not connect wwan interface')
                wwan.down()
                time.sleep(120)
                attempts = attempts + 1
                continue

            vpn.ctrl('start')
            vpn_ip = wait_for_ip(vpn_iface, timeout=30)
            if Vpn_ip is None:
                logger.error('could not connect to vpn service')
                vpn.ctrl('stop')
                wwan.down()
                time.sleep(120)
                attempts = attempts + 1
                continue
        
        if attempts >= max_attempts:
            logger.error('could not connect to server after %s attempts' %(max_attempts))
            wwan.down()
            vpn.ctrl('stop')
            self.server_connected = False
            return 1
        else:
            print('Connection to server established')
            logger.info('Connection to server established')
            self.server_connected = True
            return (ret, wwan, vpn)

    def disconnect_server(self, wwan, vpn):
        """Disconnects from the DLM server."""
        vpn.ctrl('stop')
        wwan.down()

        logger.info('Disconnected from server')
        return 0

    def upload_status(self):
        """upload a status file to the dlm server."""
        url = self.config.get('config', 'status_upload_url')
        status = Status(self.config)
        status.write_xml('current_status.xml')

        ret = system.http.post(url=url, file='current_status.xml')
        if ret is not '200':
            return 1

        logger.info('status upload successful')
        return 0

    def upload_dataset(self):
        """upload a dataset to the dlm server"""
        url = self.config.get('config', 'data_upload_url')
        output_dir = self.config.get('config', 'worker_output_dir/dataset.xml')

        ret = system.http.post(url=url, file=output_dir+'/dataset.xml')
        if ret is not '200':
            return 1

        logger.info('data upload successful')
        return 0

    def download_config(self):
        """download a configuration file from the dlm server"""
        url = self.config.get('config', 'config_download_url')
        url = url + '/' + self.config.get('config', 'serial')
        
        ret = system.http.get(url=url, dest_file='test.test')
        if ret is not '200':
            return 1

        logger.info('config download successful')
        return 0