import logging
import os.path

import requests

logger = logging.getLogger('dlmclient')

def post(self, url, data={}, files=None, max_attempts=3):
    """Make a request using HTTP POST."""
    attempts = 0

    if files is not None:
        files = {file: (os.path.basename(file), open(file, 'rb'))}

    try:
        while attempts < max_attempts:
            r = requests.post(url, data=data, files=files)
            if r.status_code is '200':
                ret = r.status_code
                logger.info('post request to "%s" with [data=%s, files=%s] successful' %(url, data, files))
                break
            attempts = attempts + 1
    except Exception as err:
        logger.error('error while post request to "%s": %s' %(url, err))
        ret = 1

    if attempts >= max_attempts:
        logger.error('could not upload file "%s" to "%s". Server returned %s' %(file, url, r.status_code))
        ret = 1

    return ret

def get(self, url, params={}, dest_file=None):
    """Make a request using HTTP GET."""
    try:
        r = requests.get(url, params=params)
    except Exception as err:
        logger.error('error while get request to "%s": %s' %(url, err))
        return 1

    logger.info('get request to "%s" with [params=%s] successful, %s' %(url, params))
    
    if r.status_code is '200':

        if dest_file is None:
            return r.text
        else:
            with open(dest_file, 'wb') as fd:
                for chunk in r.iter_content(1024):
                    fd.write(chunk)
            return 0
    else:
        return r.status_code
