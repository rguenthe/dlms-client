from __future__ import print_function

from pprint import pprint
import time
import logging
import dlmclient.system as system

logger = logging.getLogger('dlmclient')

class Status(object):
    """DLM client status"""
    
    def __init__(self, config):
        """Initialize Status instance with default values."""
        self.config = config
        self.status = {
            'serial':'None',
            'timestamp':'None',
            'uptime':'None',
            'free_disk_space_sdcard':'None',
            'free_disk_space_stick':'None',
            'wwan_reception':'None',
            'log':'None',
        }
        self.collect()

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

    def collect(self):
        """update status by reading information from the system."""
        self.status['serial'] = self.config.get('config', 'serial')
        self.status['timestamp'] = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        self.status['uptime'] = system.stats.uptime()
        self.status['free_disk_space_sdcard'] = system.stats.disk_usage('root')
        self.status['free_disk_space_stick'] = system.stats.disk_usage('sda1')
        self.status['wwan_reception'] = system.interfaces.WwanInterface.signal_strength('wwan0')

    def write_xml(self, xmlfile):
        """export current status to a xml file."""
        system.xml.write_file(xmlfile, self.status, 'status')