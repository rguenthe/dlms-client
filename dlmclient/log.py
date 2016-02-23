import logging
import logging.handlers

def setup_logger(name, logfile, loglevel=logging.DEBUG):
	log_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1048576, backupCount=5)
	formatter = logging.Formatter('%(asctime)s %(levelname)s: %(module)s: %(funcName)s: %(message)s')
	log_handler.setFormatter(formatter)
	logger = logging.getLogger(name)
	logger.addHandler(log_handler)
	logger.setLevel(loglevel)
	