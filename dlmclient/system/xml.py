from __future__ import print_function

import os.path
import logging
import lxml.etree as ET
import logging

logger = logging.getLogger('dlmclient')

def readXmlFile(filepath):
	content_dict = {}
	if os.path.isfile(filepath):
		xmltree = ET.parse(filepath)
		for item in xmltree.getroot():
			content_dict[item.tag] = item.text
		logger.info('Successfully read xml file "%s"' %(filepath))
	else:
		logger.error('Could not open file "%s"' %(filepath))

	return content_dict

def writeXmlFile(content_dict, filepath, root='file'):
	xmlroot = ET.Element(root)
	xmltree = ET.ElementTree(xmlroot)

	for key in sorted(content_dict.keys()):
		item = ET.SubElement(xmlroot, key)
		item.text = content_dict[key]
	try:
		xmltree.write(filepath, xml_declaration=True, encoding='utf-8', pretty_print=True)
	except IOError:
		logger.error('Could not write file "%s"' %(filepath))