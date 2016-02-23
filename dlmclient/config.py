from __future__ import print_function

import os.path
import logging
import lxml.etree as ET
import logging
import configparser
import dlmclient.system.xml as xml

logger = logging.getLogger('dlmclient')

class Config(object):
	
	def __init__(self, configfile='/etc/dlmclient.conf'):
		self.configfile = configfile
		self.config = configparser.ConfigParser()
		self.config.read(self.configfile)

	def get(self, section, key):
		self.config.get(section, key)

	def set(self, section, key, value):
		self.config[section][key] = value

	def updateFromXml(self, xmlfile):
		xml_conf = xml.readXmlFile(xmlfile)
		if 'config' not in self.config.sections():
			self.config['config'] = {}
			
		for key in xml_conf.keys():
			self.set('config', key, str(xml_conf[key]))

		with open(self.configfile, 'w') as configfile:
			self.config.write(configfile)
		logger.info('updated configuration from "%s"' %(xmlfile))

