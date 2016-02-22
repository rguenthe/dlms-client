import logging

def setup_logger(name, logfile):
	logging.basicConfig(	filename=logfile,
				format='%(asctime)s: %(name)s: %(levelname)s: %(module)s: %(message)s',
				datefmt='%H:%M:%S',
				level=logging.DEBUG)
	logger = logging.getLogger(name)