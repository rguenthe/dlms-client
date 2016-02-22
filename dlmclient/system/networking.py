from __future__ import print_function

import sys
import subprocess
import logging

logger = logging.getLogger('dlmclient')

def getIP(iface):
	(ret, out) = subprocess.getstatusoutput('ifconfig %s' %(iface))
	if ret is not 0:
		logger.error('Could not get ip address of interface "%s": %s' %(iface, out))
	else:
		config = out.split()
		ip = config[config.index('inet')+1]
		netmask = config[config.index('netmask')+1]
		logger.info('%s: IP address: %s, netmask: %s' %(iface, ip, netmask))
	return (ip,netmask)

def openvpnCtrl(action):
	if action is not in ['start', 'stop', 'restart']:
		logger.error('Unknown action %s' %(action))
		return 1

	(ret, out) = subprocess.getstatusoutput('/etc/init.d/openvpn %s' %(action))
	if ret is not 0:
		logger.error('Could not start openvpn: %s' %(out))
	else:
		logger.info('Started openvpn')
	return ret

class Interface(object):

	def __init__(self, iface):
		self.iface = iface
		self.ip = '0.0.0.0'
		self.netmask = '0.0.0.0'

	def up(self):
		(ret, out) = subprocess.getstatusoutput('ifup %s' %(self.iface))
		if ret is not 0:
			logger.error('Could not enable interface "%s": %s' %(self.iface, out))
		else:
			logger.info('Enabled interface %s' %(self.iface))
			self.ip, self.netmask = getIP(self.iface)
		return ret

	def down(self):
		(ret, out) = subprocess.getstatusoutput('ifdown %s' %(self.iface))
		if ret is not 0:
			logger.error('Could not disable interface "%s": %s' %(self.iface, out))
		else:
			logger.info('Disabled interface %s' %(self.iface))
		return ret
