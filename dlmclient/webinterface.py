#!/usr/bin/python

from __future__ import print_function

class Webinterface(object):
	"""DLM client Webinterface for communication with the DLM webservice."""
	
	def __init__(self, dlmclient):
		"""Initialize Webinterface instance."""
		self.dlmclient = dlmclient