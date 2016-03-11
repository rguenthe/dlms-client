import os.path
import logging
import subprocess
import time
from fileinput import FileInput

log = logging.getLogger('dlmclient')


def get_ip(iface):
    """Return the IP of the given interface."""
    ip = None
    try:
        out = subprocess.check_output('ifconfig %s' %(iface), shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        log.error('Could not get ip address of interface "%s": %s' %(iface, err))
        return None
    
    ifconfig = out.split()
    try:
        ip = ifconfig[ifconfig.index('inet')+1]
    except ValueError as err:
        log.error('Could not get ip address of interface "%s": %s' %(iface, err))
        return None

    ip = ip.strip('addr:')
    log.info('%s: IP address: %s, ' %(iface, ip))

    return ip


def wait_for_ip(iface, timeout=10):
    """Wait for an interface to get a valid IP address with timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        ip = get_ip(iface)
        if ip is None:
            log.warning('waiting for IP address...')
            time.sleep(1)
        else:
            return ip

    log.error('%s: could not get IP address. Reached timeout' %(iface))
    return None


class Interface(object):
    """Network Interface"""

    def __init__(self, iface):
        """Initialize interface with default values."""
        self.iface = iface
        self.ip = '0.0.0.0'

    def up(self):
        """Enable the interface by calling 'ifup'."""
        try:
            subprocess.check_call('ifup %s' %(self.iface), shell=True)
        except subprocess.CalledProcessError as err:
            log.error('Could not enable interface "%s": %s' %(self.iface, err))
            return 1
        log.info('Enabled interface %s' %(self.iface))
        self.ip = get_ip(self.iface)

        return 0

    def down(self):
        """Disable the interface by calling 'ifdown'."""
        try:
            subprocess.check_call('ifdown %s' %(self.iface), shell=True)
        except subprocess.CalledProcessError as err:
            log.error('Could not disable interface "%s": %s' %(self.iface, err))
            return 1
        log.info('Disabled interface %s' %(self.iface))

        return 0

    def isUp(self):
        """Check if the interface is already active by parsing output of 'ifconfig'"""
        try:
            subprocess.check_call('ifconfig | grep -E "%s"' %(self.iface), shell=True)
        except subprocess.CalledProcessError as err:
            log.error('interface "%s" is not up: %s' %(self.iface, err))
            return False
        
        log.info('interface %s is up' %(self.iface))

        return True
        

class WwanInterface(Interface):
    """WWAN network interface. Uses libqmi to communicate with the modem"""

    def __init__(self, iface):
        """Initialize WwanInterface instance."""
        super().__init__(iface)
        self.pin = None
        self.apn = None
        self.wdm_device = '/dev/cdc-wdm%s' % (iface.strip('wwan'))
        self.configured = False

    def configure(self, apn, pin):
        """Configure the interface by setting APN and verifying PIN."""
        r1 = self.setup_apn(apn)
        r2 = self.verify_pin(pin)
        ret = (r1 or r2)
        
        if ret is 0:
            self.configured = True

        return ret

    def setup_apn(self, apn):
        """
        Setup the APN for internet connection by editing the '/etc/network/interfaces' file.
        :param apn: the internet APN for the WWAN interface
        """
        try:
            for line in FileInput('/etc/network/interfaces', inplace=1):
                if 'wwan_apn' in line:
                    line = '    wwan_apn "%s"\n' %(apn)
                print(line, end='')
        except FileNotFoundError as err:
            log.error('Could not setup APN %s for "%s": %s' %(apn, self.iface, err))
            return 1
        
        self.apn = apn  
        log.info('Setup APN %s for "%s"' %(apn, self.iface))

        return 0

    def verify_pin(self, pin):
        """Unlock the SIM card using the given PIN."""
        if not os.path.exists(self.wdm_device):
            log.error('Error verifying WWAN SIM pin. No wdm device present')
            return 1
        try:
            subprocess.check_call('/usr/bin/qmicli -d %s --dms-uim-verify-pin="PIN,%s"' %(self.wdm_device, pin), shell=True)
        except subprocess.CalledProcessError as err:
            log.error('%s: pin verification failed: %s' %(self.iface, err))
            return 1

        log.info('%s: pin verification successful' %(self.iface))
        self.pin = pin

        return 0

    def signal_strength(iface):
        """Return current signal strength of the wwan device."""
        signal_strength = 'None'
        wdm_device = '/dev/cdc-wdm%s' % (iface.strip('wwan'))
        if not os.path.exists(wdm_device):
            log.error('Error reading WWAN signal strength. No wdm device present')
            return signal_strength
        try:
            out = subprocess.check_output('/usr/bin/qmicli -d %s --nas-get-signal-strength' %(wdm_device), shell=True).decode('utf-8')
        except subprocess.CalledProcessError as err:
            log.error('%s: getting signal strength failed: %s' %(iface, err))
            return signal_strength
        
        if out is not None:
            for line in out.split('\n'):
                if 'Network' in line:
                    signal_strength = line.strip()

        return signal_strength
