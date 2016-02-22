
from __future__ import print_function

import os
import sys
import subprocess
import time
import re
import logging

logger = logging.getLogger('dlmclient')

class Stats(object):

	def __init__(self):
		self.uptime = 0
		self.disk_usage = {}
		self.mem_info = {}
		self.cpu_load = 0
		self.gsm_info = {}

	def updateStats(self):
		self.uptime = self.getUptime()
		self.disk_usage = self.getDiskusage()
		self.mem_usage = self.getMeminfo()
		#self.cpu_load = getCpuload()
		#self.gsm_info = getGsminfo()

	def getUptime(self):
		cmd = 'uptime'
		(ret, out) = subprocess.getstatusoutput(cmd)
		if ret < 0:
			logger.error('Error updating uptime: Could ne execute "%s"' %(cmd), e, file=sys.stderr)
		else:
			self.uptime = re.sub(' +', ' ', out.strip())
			logger.info('updated uptime')
		return self.uptime

	def getDiskusage(self, devices=['root', 'sda']):
		for dev in devices: 
			cmd = 'df | grep -E "%s"' %(dev)
			(ret, out) = subprocess.getstatusoutput(cmd)
			if ret < 0:
				logger.error('Error updating disk_usage: Could ne execute "%s"' %(cmd), e, file=sys.stderr)
			else:
				self.disk_usage[dev] = out
		logger.info('updated disk_usage')
		return self.disk_usage

	def getMeminfo(self):
		cmd = 'free | grep -E "Mem|total"'
		(ret, out) = subprocess.getstatusoutput(cmd)
		if ret < 0:
			logger.error('Error updating uptime: Could ne execute "%s"' %(cmd), e, file=sys.stderr)
		else:
			out = out.split('\n')
			keys = out[0].split()
			values = out[1].strip('Mem:').split()
			self.mem_info = dict(zip(keys, values))
			logger.info('updated mem_info')
		return self.mem_info