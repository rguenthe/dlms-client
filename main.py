from __future__ import print_function

import sys
import argparse
import logging

import dlmclient

logger = dlmclient.log.setup_logger('dlmclient', '.dlmclient.log', logging.DEBUG)
logger = logging.getLogger('dlmclient')

def main():
	parser = argparse.ArgumentParser(description='DLM-Client: Datalogger Management Client. Communicates with the DLM webservice and controls data logging application')
	args = parser.parse_args()

	dlmc = dlmclient.Dlmclient()

	return 0

if __name__ == "__main__":
	try:
		ret = main()
	except Exception:
		ret = 1
		import traceback
		traceback.print_exc(5)
	sys.exit(ret)