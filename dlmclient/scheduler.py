import logging
import sched
import time
import datetime
import logging
import threading

logger = logging.getLogger('dlmclient')

class TaskScheduler(sched.scheduler):
    """Event scheduler that runs in a separate thread."""

    def get_run_thread(self, daemon=False):
        """Return thread that runs the "run" function of the scheduler"""
        thread = threading.Thread(target=self.run)
        return thread

    def enter_day_multiple(self, schedule, func, argument=(), kwargs={}):
        """Enter multiple events for the current day with the given schedule"""
        events = []
        today = datetime.date.fromtimestamp(time.time())
        for ev_time in schedule:
            event_time = time.strptime('%s %s-%s-%s' %(ev_time, today.year, today.month, today.day), '%H:%M %Y-%m-%d')
            event_delay = time.mktime(event_time) - time.time()

            event = self.enter(event_delay, 1, func, argument, kwargs)
            logger.info('scheduled new event today %s with function %s' %(ev_time, func))
            events.append(event)

        return events