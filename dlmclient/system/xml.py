import os.path
import lxml.etree as ET
import logging

log = logging.getLogger('dlmclient')


def read_file(filepath):
    """Read the content of an XML file into a dictonary."""
    content_dict = {}
    if os.path.isfile(filepath):
        xmltree = ET.parse(filepath)
        for item in xmltree.getroot():
            content_dict[item.tag] = item.text
        log.info('Successfully read xml file "%s"' %(filepath))
    else:
        log.error('Could not open file "%s"' %(filepath))

    return content_dict


def write_file(filepath, content_dict, root):
    """Write an XML file with content from the given dictonary."""
    xmlroot = ET.Element(root)
    xmltree = ET.ElementTree(xmlroot)

    for key in sorted(content_dict.keys()):
        item = ET.SubElement(xmlroot, key)
        item.text = content_dict[key]
    try:
        xmltree.write(filepath, xml_declaration=True, encoding='utf-8', pretty_print=True)
        log.info('Successfully wrote xml file "%s"' %(filepath))
    except IOError:
        log.error('Could not write file "%s"' %(filepath))