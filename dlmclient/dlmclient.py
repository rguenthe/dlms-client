from __future__ import print_function

import os
import sys
import logging

from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.worker import Worker
from dlmclient.webinterface import Webinterface
from dlmclient.maintenance import Maintenance

class Dlmclient(object):

	def __init__(self, logfile='.dlmclient.log'):
		self.config = Config('testfiles/dlmclient.conf')
		self.status = Status()
		self.worker = Worker()
		self.webinterface = Webinterface()
		self.maintenance = Maintenance()
		self.logger = logging.getLogger('dlmclient')
