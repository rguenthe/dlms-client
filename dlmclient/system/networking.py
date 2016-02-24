from __future__ import print_function

import os.path
import sys
import subprocess
import logging
import fileinput

logger = logging.getLogger('dlmclient')

def getIP(iface):
	ip = None
	netmask = None
	(ret, out) = subprocess.getstatusoutput('ifconfig %s' %(iface))
	if ret is not 0:
		logger.error('Could not get ip address of interface "%s": %s' %(iface, out))
	else:
		config = out.split()
		ip = config[config.index('inet')+1]
		netmask = config[config.index('netmask')+1]
		logger.info('%s: IP address: %s, netmask: %s' %(iface, ip, netmask))
	return (ip,netmask)

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

	def __init__(self, iface):
		super().__init__(iface)
		self.pin = None
		self.apn = None
		self.wdm_device = None
		self.interfaces_file = '/etc/network/interfaces'

	def up(self):
		if self.pin or self.apn is None:
			logger.error('Could not enable modem %s, PIN or APN is not configured' %(self.iface))
			return 1
		r1 = self.qmiNetworkCtrl('start')
		r2 = super().up()
		return (r1 or r2)

	def down(self):
		r1 = self.qmiNetworkCtrl('stop')
		r2 = super().down()
		return (r1 or r2)

	def configure(self, apn, pin):
		r1 = self.setupWDM()
		r2 = self.setupAPN(apn)
		r3 = self.verifyPIN(pin)
		return (r1 or r2 or r3)

	def setupAPN(self, apn):
		try:
			for line in fileinput.FileInput(self.interfaces_file, inplace=1):
				if 'wwan_apn' in line:
					line = '    wwan_apn "%s"\n' %(apn)
				print(line, end='')
			self.apn = apn	
			logger.info('Setup APN %s for "%s"' %(apn, self.iface))
		except FileNotFoundError as err:
			logger.error('Could not setup APN %s for "%s": %s' %(apn, self.iface, err))
			return 1

	def setupWDM(self):
		wdm_device = '/dev/cdc-wdm0'
		(ret, out) = subprocess.getstatusoutput('eject /dev/sr0')
		if ret is not 0:
			logger.error('Could not switch to modem mode: %s' %(out))
			return ret
		if not os.path.exists(wdm_device):
			logger.error('Could not switch to modem mode. Device %s does not exist' %(self.wdm_device))
			return 1
		logger.info('Switched to modem mode')
		self.wdm_device = wdm_device
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

	def verifyPIN(self, pin):
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

