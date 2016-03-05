from __future__ import print_function

from pprint import pprint
import time
import logging
import dlmclient.system as system

logger = logging.getLogger('dlmclient')

class Status(object):
    """DLM client status"""
    
    def __init__(self, dlmclient):
        """Initialize Status instance with default values."""
        self.dlmclient = dlmclient
        self.status = {
            'serial':'None',
            'timestamp':'None',
            'uptime':'None',
            'free_disk_space_sdcard':'None',
            'free_disk_space_stick':'None',
            'gsm_reception':'None',
            'log':'None',
        }

    def set(self, key, value):
        """Set a value in the status dictonary."""
        try:
            self.status[key] = value
            logger.info('updated %s to %s' %(key, value))
            ret = 0
        except KeyError as err:
            logger.error('could not update %s to %s: %s' %(key, value, err))
            ret = 1
        return ret

    def get(self, key):
        """Get a value from the status dictonary."""
        try:
            ret = self.status[key] = value
            logger.info('read %s' %(key))
        except KeyError as err:
            logger.error('could not read %s: %s' %(key, err))
            ret = 1
        return ret

    def update(self):
        """update status by reading information from the system."""
        self.status['serial'] = self.dlmclient.config.get('config', 'serial')
        self.status['timestamp'] = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        self.status['uptime'] = system.stats.uptime()
        self.status['free_disk_space_sdcard'] = system.stats.disk_usage('root')
        self.status['free_disk_space_stick'] = system.stats.disk_usage('sda1')
        self.status['gsm_reception'] = self.dlmclient.wwan.signal_strength()
        print(self.status)

    def write_xml(self, xmlfile):
        """export current status to a xml file."""
        system.xml.write_file(xmlfile, self.status, 'status')