import logging
import sched
from dlmclient.system.threads import FuncThread

logger = logging.getLogger('dlmclient')
            
class TaskScheduler(sched.scheduler):
    """Event scheduler that runs in a separate thread."""

    def run_threaded(self, daemon=False):
        thread = FuncThread(self.run)
        thread.daemon = daemon
        thread.start()

        return thread
