import logging
import os.path

import requests

log = logging.getLogger('dlmclient')


def post(url, data={}, file=None, max_attempts=3):
    """Make a request using HTTP POST."""
    attempts = 0
    files = {}

    if file is not None:
        files = {file: (os.path.basename(file), open(file, 'rb'))}

    try:
        while attempts < max_attempts:
            r = requests.post(url, data=data, files=files)
            if r.status_code is '200':
                ret = r.status_code
                log.info('request to "%s" with data=%s, files=%s successful' %(url, data, files))
                break
            attempts += 1
    except Exception as err:
        log.error('error while post request to "%s": %s' %(url, err))
        ret = 1

    if attempts >= max_attempts:
        log.error('request to "%s" with data=%s, files=%s failed. Server returned %s' %(url, data, files, r.status_code))
        ret = 1

    return ret


def get(url, params={}, dest_file=None):
    """Make a request using HTTP GET."""
    try:
        r = requests.get(url, params=params)
    except Exception as err:
        log.error('error while get request to "%s": %s' %(url, err))
        return 1
    
    if r.status_code is '200':
        log.info('request to "%s" with params=%s successful' %(url, params))
        if dest_file is None:
            return r.text
        else:
            with open(dest_file, 'wb') as fd:
                for chunk in r.iter_content(1024):
                    fd.write(chunk)
            return 0
    else:
        log.error('request to "%s" with params=%s failed. Server returned %s' %(url, params, r.status_code))
        return r.status_code
