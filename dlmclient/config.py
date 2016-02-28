from __future__ import print_function

import os.path
import logging
import lxml.etree as ET
import logging
import configparser
import dlmclient.system.xml as xml

logger = logging.getLogger('dlmclient')

class Config(object):
	"""DLM client configuration interface."""
	
	def __init__(self, configfile='/etc/dlmclient.conf'):
		"""Initialize Config instance using the given configuration file."""
		self.configfile = configfile
		self.config = configparser.ConfigParser()
		self.config.read(self.configfile)

	def get(self, section, key):
		"""return value an option in the configuration file."""
		value = self.config.get(section, key)
		if value is None:
			logger.error('could not get option "%s" from section [%S]' %(key, section))
		return value

	def set(self, section, key, value):
		"""set value in the configuration file."""
		try:
			ret = self.config.set(section, key, value)
			logger.info('set "%s" in section [%s] to "%s"' %(key, section, value))
		except Exception as err:
			ret = 1
			logger.error('could not set "%s" in section [%s] to "%s": %s' %(key, section, value, err))
		return ret

	def updateFromXml(self, xmlfile, section='config'):
		"""update current configuration file by reading values from a xml file."""
		xml_conf = xml.readXmlFile(xmlfile)
		if section not in self.config.sections():
			self.config[section] = {}
			
		for key in xml_conf.keys():
			self.set(section, key, str(xml_conf[key]))

		with open(self.configfile, 'w') as configfile:
			self.config.write(configfile)
		logger.info('updated configuration from "%s"' %(xmlfile))

