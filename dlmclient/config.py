#!/usr/bin/python

from __future__ import print_function

import os.path
import logging
import lxml.etree as ET

class Config(object):
	
	def __init__(self, logger, conffilepath='/etc/dlmclient.xml'):
		self.logger = logger
		self.xmlfilepath = os.path.abspath(conffilepath)
		self.initialized = False
		self.fields = {
			'serial':'',
			'active':'',
			'worker_exec_path':'',
			'worker_exec_option':'',
			'status_upload_interval':'',
			'status_upload_url':'',
			'data_upload_interval':'',
			'data_upload_url':'',
			'maintenance_stay_online':'',
			'maintenance_wifi':''
		}
		self.readConfig()
		self.writeConfig()

	def readConfig(self):
		if os.path.isfile(self.xmlfilepath):
			xmltree = ET.parse(self.xmlfilepath)
			xmlroot = xmltree.getroot()

			for key in self.fields.keys():
				self.fields[key] = xmlroot.find(key).text

			self.initialized = True
			self.logger.info('config: Successfully read xml config file "%s"' %(self.xmlfilepath))
		else:
			self.logger.error('config: Could not find config file "%s"' %(self.xmlfilepath))

	def writeConfig(self, destpath='/etc/_dlmclient.xml', root='config'):
		xmlroot = ET.Element(root)
		xmltree = ET.ElementTree(xmlroot)

		for key in sorted(self.fields.keys()):
			item = ET.SubElement(xmlroot, key)
			item.text = self.fields[key]

		try:
			xmltree.write(destpath, xml_declaration=True, encoding='utf-8', pretty_print=True)
		except IOError:
			self.logger.error('config: Could not write config file to "%s"' %(destpath))