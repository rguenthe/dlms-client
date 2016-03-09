import os
import json
import logging

logger = logging.getLogger('dlmclient')

class Config(object):
    """DLM client configuration interface (JSON)."""
    
    def __init__(self, configfile='/etc/dlmclient.json'):
        """Initialize Config instance using the given configuration file."""
        self.configfile = configfile
        self.dict = None
        self.read()

    def read(self):
        with open(self.configfile, 'r') as fp:
            self.dict = json.load(fp)
            fp.close()

    def get(self, section, key):
        """return value an option in the configuration file."""
        try:
            value = self.dict[section][key]
            logger.info('from section [%s] read "%s"' %(section, key))
        except Exception as err:
            value = ''
            logger.error('could not read option "%s" from section [%s]: %s' %(key, section, err))
        
        return value

    def set(self, section, key, value):
        """set value in the configuration file."""
        try:
            self.dict[section][key] = value
            logger.info('in section [%s] set "%s" to "%s"' %(section, key, value))
        except Exception as err:
            ret = 1
            logger.error('could not set "%s" in section [%s] to "%s": %s' %(key, section, value, err))
        
        return ret

    def update_dlmconfig(self, jsonfile, section='dlmconfig'):
        """update current configuration file by reading values from JSON file."""
        if not os.path.exists(jsonfile):
            logger.error('could not update configuration: File "%s" does not exists' %(jsonfile))
            return 1

        with open(jsonfile, 'r') as fp:
            update_dict = json.load(fp)
            fp.close()

        for key in update_dict['dlmconfig'].keys():
            self.dict['dlmconfig'][key] = update_dict['dlmconfig'][key]

        with open(self.configfile, 'w') as fp:
            json.dump(self.dict, fp, sort_keys=True, indent=4)
            fp.close()
        
        logger.info('updated configuration from "%s"' %(jsonfile))
        return 0
