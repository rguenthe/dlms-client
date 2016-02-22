#!/usr/bin/python

from __future__ import print_function

import os
import sys
import logging

from status import Status
from config import Config
from worker import Worker
from webinterface import Webinterface
from maintenance import Maintenance

class Dlmclient(object):

	def __init__(self, logfile='.dlmclient.log'):
		logging.basicConfig(	filename=logfile,
					format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
					datefmt='%H:%M:%S',
					level=logging.DEBUG)
		self.logger = logging.getLogger('dlmclient')

		self.config = Config(self.logger, '../testfiles/config.xml')
		self.status = Status()
		self.worker = Worker()
		self.webinterface = Webinterface()
		self.maintenance = Maintenance()
		self.logger = logging.getLogger('dlmclient')
