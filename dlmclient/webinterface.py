import os.path
import logging

import requests

from dlmclient.system.service import SystemService
from dlmclient.system.networking import WwanInterface, wait_for_ip

logger = logging.getLogger('dlmclient')

class Webinterface(object):
    """DLM client Webinterface for communication with the DLM server."""
    
    def __init__(self, dlmclient):
        """Initialize Webinterface instance."""
        self.config = dlmclient.config
        self.wwan = WwanInterface(self.config.get('wwan', 'iface'))
        self.wwan.configure(apn=self.config.get('wwan', 'apn'), 
                            pin=self.config.get('wwan', 'pin'))
        self.vpn = SystemService(self.config.get('vpn', 'service'))

    def upload_status(self, file):
        """upload a status file to the dlm server."""
        url = self.config.get('config', 'status_upload_url')
        ret = self.__upload_file_post(url, file=file)

        return ret

    def upload_dataset(self, file):
        """upload a dataset to the dlm server"""
        url = self.config.get('config', 'data_upload_url')
        ret = self.__upload_file_post(url, file=file)

        return ret

    def download_config(self, dest_file):
        """download a configuration file from the dlm server"""
        url = self.config.get('config', 'config_download_url')
        url = url + '/' + self.config.get('config', 'serial')
        ret = self.__download_file(url, dest_file)

        return ret

    def __upload_file_post(self, url, file, max_attempts=3):
        """Upload a file using HTTP POST."""
        files = {file: (os.path.basename(file), open(file, 'rb'))}
        attempts = 0

        try:
            while attempts < max_attempts:
                r = requests.post(url, files=files)
                if r.status_code is '200':
                    ret = 0
                    logger.info('post request to "%s" with file=%s successful' %(url, files))
                    break
                attempts = attempts + 1
        except Exception as err:
            logger.error('error while post request to "%s": %s' %(url, err))
            ret = 1

        if attempts >= max_attempts:
            logger.error('could not upload file "%s" to "%s". Server returned %s' %(file, url, r.status_code))
            ret = 1

        return ret

    def __download_file(self, url, dest_file):
        """Download a file using HTTP GET."""
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