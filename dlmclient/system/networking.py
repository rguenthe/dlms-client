from __future__ import print_function

import os.path
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
	if action not in ['start', 'stop', 'restart']:
		logger.error('Unknown action %s' %(action))
		return 1

	(ret, out) = subprocess.getstatusoutput('/etc/init.d/openvpn %s' %(action))
	if ret is not 0:
		logger.error('%s openvpn failed: ' %(action, out))
	else:
		logger.info('%s openvpn' %(action))
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

class GsmModem(Interface):

	def __init__(self, iface, pin):
		self.iface = iface
		self.ip = '0.0.0.0'
		self.netmask = '0.0.0.0'
		self.wdm_device = None
		self.pin = pin

	def up_configured(self):
		self.setModemMode()
		self.verifyPin(self.pin)
		self.qmiNetworkCtrl('start')
		self.up()

	def setModemMode(self):
		wdm_device = '/dev/cdc-wdm0'
		(ret, out) = subprocess.getstatusoutput('eject /dev/sr0')
		if ret is not 0:
			logger.error('Could not switch to modem mode: %s' %(out))
			return ret
		if os.path.exists(wdm_device):
			logger.info('Switched to modem mode')
			self.wdm_device = wdm_device
		else:
			logger.error('Could not switch to modem mode. Device %s does not exist' %(self.wdm_device))
			return 1
		return ret

	def qmiNetworkCtrl(self, action):
		if action not in ['start', 'stop']:
			logger.error('Unknown action %s' %(action))
			return 1
		(ret, out) = subprocess.getstatusoutput('/usr/bin/qmi-network %s %s' %(self.wdm_device, action))
		if ret is not 0:
			logger.error('%s qmi-network failed: %s' %(action, out))
		else:
			logger.info('%s qmi-network' %(action))
		return ret	

	def verifyPin(self, pin):
		if self.wdm_device is None:
			logger.error('No modem device present')
			return 1
		(ret, out) = subprocess.getstatusoutput('/usr/bin/qmicli -d %s --dms-uim-verify-pin="PIN,%s"' %(self.wdm_device, pin))
		if ret is not 0:
			logger.error('%s: pin verification failed: %s' %(self.iface, out))
		else:
			logger.info('%s: pin verification successful' %(self.iface))
			self.pin = pin
		return ret

