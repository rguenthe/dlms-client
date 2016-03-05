#!/usr/bin/python

from __future__ import print_function

import os
import subprocess
import threading
import logging

logger = logging.getLogger('dlmclient')

class CmdThread(threading.Thread):
    """Execute a command in a separate Thread."""
    
    def __init__(self, cmd):
        """Initialize CmdThread with the given command."""
        self.cmd = cmd
        super().__init__()

    def run(self):
        """Start the Thread."""
        logger.info('Starting worker thread with command %s' %(self.cmd))
        (ret, out) = subprocess.check_output(self.cmd, shell=True)
        
        if ret is not 0:
            logger.error('Error while executing worker thread %s: %s' %(self.cmd, out))

class FuncThread(threading.Thread):
    """Execute a python function in a separate thread"""
    
    def __init__(self, func, args=(), kwargs={}):
        """Initialize Task with the given function."""
        self.func = func
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def run(self):
        """Start the Thread."""
        try:
            logger.info('Executing function "%s%s" in separate thread ' %(self.func.__name__, self.args))
            self.func(*self.args, **self.kwargs)
        except Exception as err:
            logger.error('Error executing function "%s%s" in thread: %s' %(self.func.__name__, self.args, err))
