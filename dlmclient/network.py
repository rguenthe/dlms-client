import time
import logging

import dlmclient.system as system
from dlmclient.system.interfaces import wait_for_ip

log = logging.getLogger('dlmclient')


class Network(object):
    """
    Simple network connection representation
    """

    def __init__(self, iface, wwan=False, wwan_apn='', wwan_pin=''):
        """Initialize a new network instance."""
        if wwan:
            self.iface = system.interfaces.WwanInterface(iface)
            self.iface.configure(apn=wwan_apn, pin=wwan_pin)
        else:
            self.iface = system.interfaces.Interface(iface)
        self.ip = None
        self.connect_timeout = 10
        self.connect_retry_interval = 10
        self.connected = False
        self.max_connection_duration = 300
        self.wwan_apn = wwan_apn
        self.wwan_pin = wwan_pin

    def connect(self, max_attempts=3):
        """Initiates a connection to the network."""
        attempts = 0

        while attempts < max_attempts:
            print("Attempt network connection using interface %s" %(self.iface.iface))
            self.iface.up()

            ip = wait_for_ip(self.iface.iface, timeout=self.connect_timeout)
            if ip is None:
                log.error('could not connect interface %s' %(self.iface.iface))
                self.disconnect()

                time.sleep(self.connect_retry_interval)
                attempts = attempts + 1
                continue
            else:
                log.info('got ip %s for interface %s' %(self.ip, self.iface.iface))
                break
        
        if attempts >= max_attempts:
            log.error('could not connect to network after %s attempts' %(max_attempts))
            self.disconnect()
            return 1

        print('network connection established')
        log.info('network connection established')
        self.ip = ip
        self.connected = True

        return 0

    def disconnect(self):
        """Disconnects from the network."""
        if self.connected:
            self.iface.down()
            self.connected = False
            self.ip = None
            log.info('disconnected from network')
        else:
            log.info('already disconnected. Doing nothing.')

        return 0


class OpenvpnNetwork(Network):
    """
    Representation of an OpenVpn network.
    """

    def __init__(self, iface, vpn_iface, vpn_service, wwan=False, wwan_apn='', wwan_pin=''):
        """Initialize a openvpn network."""
        self.vpnservice = system.service.SystemService(vpn_service)
        self.vpn_iface = vpn_iface
        self.vpn_connect_timeout = 30
        self.vpn_ip = None
        super().__init__(iface, wwan, wwan_apn, wwan_pin)

    def configure(self, config, wwan_inet=False):
        super().configure(wwan_inet)
        self.vpnservice = system.service.SystemService(service=self.config.get('network', 'vpn_service'))
        self.vpn_iface = self.config.get('network', 'vpn_iface')

    def connect(self):
        """Connect to openvpn network."""
        ret = super().connect()
        if ret is not 0:
            return 1

        ret = self.vpnservice.ctrl('start')
        if ret is not 0:
            log.error('could not start vpn service "%s"' %(self.vpnservice.service))
            return 1

        vpn_ip = wait_for_ip(self.vpn_iface, timeout=self.vpn_connect_timeout)
        if vpn_ip is None:
            log.error('could not connect to vpn service')
            self.disconnect()
            return 1
        else:
            log.info('got ip %s for interface %s' %(self.vpn_ip, self.vpn_iface))

        print('network connection established')
        log.info('network connection established')
        self.ip = vpn_ip

        return 0

    def disconnect(self):
        """Disconnect from the openvpn network."""
        self.vpnservice.ctrl('stop')
        log.info('disconnected from vpn network')

        super().disconnect()

        return 0