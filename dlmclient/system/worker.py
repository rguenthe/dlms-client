#!/usr/bin/python

from __future__ import print_function

import os
import subprocess
import threading
import logging

logger = logging.getLogger('dlmclient')

class WorkerThread(threading.Thread):
    """Execute a command in a separate Thread."""
    
    def __init__(self, cmd):
        """Initialize WorkerThread with the given command."""
        self.cmd = cmd
        super().__init__()

    def run(self):
        """Start the Thread."""
        logger.info('Starting worker thread with command %s' %(self.cmd))
        (ret, out) = subprocess.getstatusoutput(self.cmd)
        if ret is not 0:
            logger.error('Error while executing worker thread %s: %s' %(self.cmd, out))
