import subprocess
import logging

log = logging.getLogger('dlmclient')


class SystemService(object):
    """System service control"""

    def __init__(self, service):
        """Initialize SystemService instance."""
        self.service = service
        self.actions = ['start', 'stop', 'restart', 'reload', 'status']

    def ctrl(self, action):
        """Control the system service by calling the init.d script with control option."""
        if action not in self.actions:
            log.error('Unknown action %s' %(action))
            return 1

        try:
            ret = subprocess.check_call('/etc/init.d/%s %s' %(self.service, action), shell=True)
            log.info('%s %s' %(action, self.service))
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            log.error('%s %s failed: %s' %(action, self.service, err))
            return 1
            
        return 0
