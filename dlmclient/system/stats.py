from __future__ import print_function

import sys
import subprocess
import re
import logging

logger = logging.getLogger('dlmclient')

def uptime():
	"""Return the output of the 'uptime' command."""
	cmd = 'uptime'
	(ret, out) = subprocess.getstatusoutput('uptime')
	if ret is not 0:
		logger.error('Error read uptime: Could ne execute "%s"' %(cmd))
	else:
		uptime = re.sub(' +', ' ', out.strip())
		logger.info('read uptime')
	return uptime

def disk_usage(device):
	"""Return disk usage information for the given storrage device."""
	disk_usage = 'None'
	cmd = 'df | grep -E "%s"' %(device)
	(ret, out) = subprocess.getstatusoutput(cmd)
	if ret is not  0:
		logger.error('Error read disk usage: Could ne execute "%s"' %(cmd))
	else:
		disk_usage = re.sub(' +', ' ', out.strip())
		logger.info('read disk_usage')
	return disk_usage

def mem_info():
	"""Return memory information."""
	cmd = 'free | grep -E "Mem|total"'
	(ret, out) = subprocess.getstatusoutput(cmd)
	if ret is not  0:
		logger.error('Error read uptime: Could ne execute "%s"' %(cmd))
	else:
		out = out.split('\n')
		keys = out[0].split()
		values = out[1].strip('Mem:').split()
		mem_info = dict(zip(keys, values))
		logger.info('read mem info')
	return mem_info