import os.path
import logging

import requests

from dlmclient.system.service import SystemService
from dlmclient.system.networking import WwanInterface

logger = logging.getLogger('dlmclient')

class Webinterface(object):
    """DLM client Webinterface for communication with the DLM server."""
    
    def __init__(self, dlmclient):
        """Initialize Webinterface instance."""
        self.config = dlmclient.config
        self.wwan = WwanInterface(self.config.get('gsm', 'iface'))
        self.wwan.configure(apn=self.config.get('gsm', 'apn'), 
                            pin=self.config.get('gsm', 'pin'))
        self.vpn = SystemService(self.config.get('vpn', 'service'))

    def upload_status(self, file):
        """upload a status file to the dlm server"""
        url = self.config.get('config', 'status_upload_url')
        ret = self.http_post_file(url, file=file)

        return ret

    def upload_data(self, file):
        """upload a dataset to the dlm server"""
        url = self.config.get('config', 'data_upload_url')
        ret = self.http_post_file(url, file=file)

        return ret

    def download_config(self, dest_file):
        """download a configuration file from the dlm server"""
        url = self.config.get('config', 'config_download_url')
        url = url + '/' + self.config.get('config', 'serial')
        ret = self.http_get_file(url, dest_file)

        return ret

    def http_post_file(self, url, file):
        """HTTP POST request with file."""
        files = {file: (os.path.basename(file), open(file, 'rb'))}
        try:
            r = requests.post(url, files=files)
        except Exception as err:
            logger.error('error while post request to "%s": %s' %(url, err))
            return 1

        logger.info('post request to "%s" with files=%s returned %s' %(url, files, r.status_code))

        return r.status_code

    def http_get_file(self, url, dest_file):
        """HTTP GET request with parameters."""
        try:
            r = requests.get(url)
        except Exception as err:
            logger.error('error while get request to "%s": %s' %(url, err))
            return 1

        logger.info('get request to "%s" returned %s' %(url, r.status_code))
        
        if r.status_code is '200':
            with open(dest_file, 'wb') as fd:
                for chunk in r.iter_content(1024):
                    fd.write(chunk)

        return r.status_code