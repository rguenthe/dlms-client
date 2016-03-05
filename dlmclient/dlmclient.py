import os
import sys
import logging

import dlmclient.system as system
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.threads import CmdThread
from dlmclient.webinterface import Webinterface

class Dlmclient(object):
    """
    Datalogger management client: 
    Uploads status reports, downloads configurations and system updates from the DLM server.
    Controls the worker application that does the actual data logging and uploads the recorded data to the DLM server.

    Argument: configfile -- path to the configuration file
    """

    def __init__(self, configfile='/etc/dlmclient.conf'):
        """Initialize Dlmclient instance using the given configuration file."""
        self.logger = logging.getLogger('dlmclient')
        self.config = Config(configfile)
        self.status = Status(self)
        self.webinterface = Webinterface(self)
        self.worker = CmdThread(self.config.get('config', 'worker_exec_path'))
