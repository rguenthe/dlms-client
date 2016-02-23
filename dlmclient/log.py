import logging

def setup_logger(name, logfile, Level=logging.DEBUG):
	logging.basicConfig(	filename=logfile,
				format='%(asctime)s %(levelname)s: %(module)s: %(funcName)s: %(message)s',
				datefmt='%H:%M:%S',
				level=Level)
	logger = logging.getLogger(name)