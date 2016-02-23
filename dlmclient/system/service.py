from __future__ import print_function

import os.path
import sys
import subprocess
import logging

logger = logging.getLogger('dlmclient')

class SystemService(object):

	def __init__(self, service):
		self.service = service
		self.actions = ['start', 'stop', 'restart', 'reload', 'status']

	def ctrl(self, action):
		if action not in self.actions:
			logger.error('Unknown action %s' %(action))
			return 1

		(ret, out) = subprocess.getstatusoutput('/etc/init.d/%s %s' %(self.service, action))
		if ret is not 0:
			logger.error('%s %s failed: %s' %(action, self.service, out))
		else:
			logger.info('%s %s' %(action, self.service))
		return ret