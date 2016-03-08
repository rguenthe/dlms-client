import logging
import sched

import dlmclient.system.http as http
from dlmclient.system.threads import FuncThread
from dlmclient.system.interfaces import WwanInterface, wait_for_ip
from dlmclient.system.service import SystemService

from dlmclient.status import Status

logger = logging.getLogger('dlmclient')

class Tasks(object):
    """Defines tasks that can be scheduled using the TaskScheduler."""

    def __init__(self, config):
        self.config = config

    def connect_server(self):
        """Initiates a connection to the DLM Server."""
        wwan = WwanInterface(self.config.get('wwan', 'iface'))
        wwan.configure(apn=self.config.get('wwan', 'apn'), 
                       pin=self.config.get('wwan', 'pin'))
        vpn = SystemService(self.config.get('vpn', 'service'))
        vpn_iface = self.config.get('vpn', 'iface')

        wwan.up()
        wwan_ip = wait_for_ip(wwan.iface)
        if wwan_ip is None:
            logger.error('could not connect wwan interface')
            ret = 1

        vpn.ctrl('start')
        vpn_ip = wait_for_ip(vpn_iface)
        if Vpn_ip is None:
            logger.error('could not connect to vpn service')
            ret = 1
        
        logger.info('Connected to server')
        ret = 0

        return (ret, wwan, vpn)

    def disconnect_server(self, wwan, vpn):
        """Disconnects from the DLM server."""
        SystemService(self.config.get('vpn', 'service')).ctrl('stop')
        WwanInterface(self.config.get('wwan', 'iface')).down()

        logger.info('Disconnected from server')

        return 0

    def upload_status(self):
        """upload a status file to the dlm server."""
        status = Status(self.config)
        status.write_xml('current_status.xml')
        
        url = self.config.get('config', 'status_upload_url')
        ret = http.post(url, files='current_status.xml')

        logger.info('Uploaded status')

        return ret

    def upload_dataset(self):
        """upload a dataset to the dlm server"""
        url = self.config.get('config', 'data_upload_url')
        ret = http.post(url, files=file)

        logger.info('Uploaded status')

        return ret

    def download_config(self):
        """download a configuration file from the dlm server"""
        url = self.config.get('config', 'config_download_url')
        url = url + '/' + self.config.get('config', 'serial')
        ret = self.http.get(url, dest_file=dest_file)

        return ret
            
class TaskScheduler(sched.scheduler):
    """Event scheduler that runs in a separate thread."""

    def run_threaded(self, daemon=False):
        thread = FuncThread(self.run)
        thread.daemon = daemon
        thread.start()

        return thread
