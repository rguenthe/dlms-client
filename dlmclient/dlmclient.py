from __future__ import print_function

import os
import sys
import logging

from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.worker import WorkerThread
from dlmclient.webinterface import Webinterface

class Dlmclient(object):

	def __init__(self):
		self.config = Config('/etc/dlmclient.conf')
		self.status = Status()
		self.worker = WorkerThread('sleep 10')
		self.webinterface = Webinterface()
		self.logger = logging.getLogger('dlmclient')
