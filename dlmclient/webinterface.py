import logging
from dlmclient.system.service import SystemService
from dlmclient.system.networking import WwanInterface

logger = logging.getLogger('dlmclient')

class Webinterface(object):
    """DLM client Webinterface for communication with the DLM server."""
    
    def __init__(self, dlmclient):
        """Initialize Webinterface instance."""
        self.config = dlmclient.config
        self.wwan = WwanInterface(self.config.get('gsm', 'iface'))
        self.vpn = SystemService(self.config.get('vpn', 'service'))

        self.wwan.configure(apn=self.config.get('gsm', 'apn'), 
							pin=self.config.get('gsm', 'pin'))
