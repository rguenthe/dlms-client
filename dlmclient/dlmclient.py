from __future__ import print_function

import os
import sys
import logging

import dlmclient.system as system
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.worker import WorkerThread
from dlmclient.system.service import SystemService
from dlmclient.system.networking import GsmModem
from dlmclient.webinterface import Webinterface

class Dlmclient(object):

	def __init__(self, configfile='/etc/dlmclient.conf'):
		self.logger = logging.getLogger('dlmclient')
		self.config = Config(configfile)
		self.status = Status(self)
		self.webinterface = Webinterface(self)
		self.wwan = GsmModem(self.config.get('gsm', 'iface'))
		self.wwan.configure(apn=self.config.get('gsm', 'apn'), pin=self.config.get('gsm', 'pin'))
		self.vpn = SystemService(self.config.get('vpn', 'service'))
		self.worker = WorkerThread(self.config.get('config', 'worker_exec_path'))
