import os
import sys
import logging
import time
import datetime

import dlmclient.system as system
from dlmclient.status import Status
from dlmclient.config import Config
from dlmclient.system.threads import CmdThread
from dlmclient.tasks import TaskScheduler, Tasks

logger = logging.getLogger('dlmclient')

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
        self.status = Status(self.config)
        self.worker = CmdThread(self.config.get('config', 'worker_exec_path'))
        self.tasks = TaskScheduler()
        self.actions = Tasks(self.config)

    def schedule_tasks(self):
        """schedule tasks as specified in the config file."""
        date = datetime.date.fromtimestamp(time.time())

        schedule = self.config.get('config', 'task_schedule')
        for event in schedule.replace(' ','').split(','):
            # calculate the time of the event
            event_time = time.strptime('%s %s-%s-%s' %(event, date.year, date.month, date.day), '%H:%M %Y-%m-%d')
            print(event_time)
            self.tasks.enterabs(time.mktime(event_time), 1, print, ('task %s' %(event),))

    def run(self):
        """Start the DLM client."""

        self.schedule_tasks()
        print('starting task scheduler')
        task_thread = self.tasks.run_threaded()
        print('starting worker thread')
        self.worker.start()

        while (self.worker.isAlive() or task_thread.isAlive()):
            time.sleep(1)

        print('Worker exited and all Tasks are done. Exit!')
