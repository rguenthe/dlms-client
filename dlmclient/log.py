import logging
import logging.handlers


def setup_logger(name, logfile, loglevel=logging.DEBUG):
    """Setup a logger with rotating logfile."""
    log_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1048576, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(module)s: %(funcName)s: %(message)s')
    log_handler.setFormatter(formatter)
    log = logging.getLogger(name)
    log.addHandler(log_handler)
    log.setLevel(loglevel)
    