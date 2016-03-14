import sched
import time
import datetime
import logging
import threading

log = logging.getLogger('dlmclient')


class TaskScheduler(sched.scheduler):
    """Event scheduler that runs in a separate thread."""

    def get_run_thread(self):
        """Return thread that runs the "run" function of the scheduler"""
        thread = threading.Thread(target=self.run)
        return thread

    def enter_schedule(self, schedule, prio, func, argument=(), kwargs={}, pre=None, post=None):
        """Enter multiple events for the current day with the given schedule"""
        events = []
        today = datetime.date.fromtimestamp(time.time())
        for ev_time in schedule:
            event_time = time.strptime('%s %s-%s-%s' %(ev_time, today.year, today.month, today.day), '%H:%M %Y-%m-%d')
            event_delay = time.mktime(event_time) - time.time()

            # only schedule future events
            if event_delay > 0:
                event = self.enter(event_delay, prio, func, argument, kwargs)
                log.info('scheduled new event today %s with function %s' %(ev_time, func.__name__))

                if pre is not None:
                    pre_ev = self.enter(event_delay-5, prio, pre)
                    log.info('scheduled pre-event function %s' %(pre.__name__))
                if post is not None:
                    post_ev = self.enter(event_delay+5, prio, post)
                    log.info('scheduled post-event function %s' %(post.__name__))

                events.append(event)

        return events
