from __future__ import print_function

import sys
import argparse
import logging

import log
from dlmclient import Dlmclient

logger = log.setup_logger('dlmclient', '.dlmclient.log')

def main():
	parser = argparse.ArgumentParser(description='DLM-Client: Datalogger Management Client. Communicates with the DLM webservice and controls data logging application')
	args = parser.parse_args()

	dlmclient = Dlmclient()

if __name__ == "__main__":
	try:
		ret = main()
	except Exception:
		ret = 1
		import traceback
		traceback.print_exc(5)
	sys.exit(ret)