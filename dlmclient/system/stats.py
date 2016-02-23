from __future__ import print_function

import sys
import subprocess
import re
import logging

logger = logging.getLogger('dlmclient')

def uptime():
	(ret, out) = subprocess.getstatusoutput('uptime')
	if ret is not 0:
		logger.error('Error read uptime: Could ne execute "%s"' %(cmd))
	else:
		uptime = re.sub(' +', ' ', out.strip())
		logger.info('read uptime')
	return uptime

def disk_usage(devices=['']):
	disk_usage = {}
	for dev in devices: 
		(ret, out) = subprocess.getstatusoutput('df -l | grep -E "%s"' %(dev))
		if ret is not  0:
			logger.error('Error read disk usage: Could ne execute "%s"' %(cmd))
		else:
			disk_usage[dev] = out.split('\n')
			logger.info('read disk_usage')
	return disk_usage

def mem_info():
	(ret, out) = subprocess.getstatusoutput('free | grep -E "Mem|total"')
	if ret is not  0:
		logger.error('Error read uptime: Could ne execute "%s"' %(cmd))
	else:
		out = out.split('\n')
		keys = out[0].split()
		values = out[1].strip('Mem:').split()
		mem_info = dict(zip(keys, values))
		logger.info('read mem info')
	return mem_info