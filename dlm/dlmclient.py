from __future__ import print_function

import os
import sys
import logging

from dlm.status import Status
from dlm.config import Config
from dlm.worker import Worker
from dlm.webinterface import Webinterface
from dlm.maintenance import Maintenance

class Dlmclient(object):

	def __init__(self, logfile='.dlmclient.log'):
		self.config = Config('testfiles/config.xml')
		self.status = Status()
		self.worker = Worker()
		self.webinterface = Webinterface()
		self.maintenance = Maintenance()
		self.logger = logging.getLogger('dlmclient')
