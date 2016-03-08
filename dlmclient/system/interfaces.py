import os.path
import subprocess
import logging
import time
from fileinput import FileInput

logger = logging.getLogger('dlmclient')

def get_ip(iface):
    """Return the IP and netmask of the given interface."""
    ip = None
    try:
        out = subprocess.check_output('ifconfig %s' %(iface), shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.error('Could not get ip address of interface "%s": %s' %(iface, err))    
        return None
    
    ifconfig = out.split()
    try:
        ip = ifconfig[ifconfig.index('inet')+1]
    except ValueError as err:
        return None

    logger.info('%s: IP address: %s, ' %(iface, ip))

    return ip

def wait_for_ip(iface, timeout=10):
    """Wait for an interface to get a valid IP address with timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        ip = get_ip(iface)
        if ip is None:
            logger.warning('waiting for IP address...')
            time.sleep(1)
        else:
            logger.info('%s: IP address: %s' %(iface, ip))
            return ip

    logger.error('%s: could not get IP address. Reached timeout' %(iface))
    return None
    


class Interface(object):
    """Network Interface"""

    def __init__(self, iface):
        """Initialize interface with default values."""
        self.iface = iface
        self.ip = '0.0.0.0'
        self.netmask = '0.0.0.0'

    def up(self):
        """Enable the interface by calling 'ifup'."""
        try:
            subprocess.check_call('ifup %s' %(self.iface), shell=True)
        except subprocess.CalledProcessError as err:
            logger.error('Could not enable interface "%s": %s' %(self.iface, err))
            return 1
        logger.info('Enabled interface %s' %(self.iface))
        self.ip, self.netmask = get_ip(self.iface)

        return 0

    def down(self):
        """Disable the interface by calling 'ifdown'."""
        try:
            subprocess.check_call('ifdown %s' %(self.iface), shell=True)
        except subprocess.CalledProcessError as err:
            logger.error('Could not disable interface "%s": %s' %(self.iface, err))
            return 1
        logger.info('Disabled interface %s' %(self.iface))

        return 0

        

class WwanInterface(Interface):
    """WWAN network interface"""

    def __init__(self, iface):
        """Initialize WwanInterface instance."""
        super().__init__(iface)
        self.pin = None
        self.apn = None
        self.wdm_device = self.get_wdm_device()
        self.configured = False

    def up(self):
        """Enable wwan interface, if it is configured."""
        if not self.configured:
            logger.error('Could not enable modem %s, PIN or APN is not configured' %(self.iface))
            return 1
        
        r1 = self.qmi_network_ctrl('start')
        r2 = super().up()

        return (r1 or r2)

    def down(self):
        """Disable wwan interface."""
        r1 = self.qmi_network_ctrl('stop')
        r2 = super().down()
        
        return (r1 or r2)

    def configure(self, apn, pin):
        """Configure the interface by setting APN and verifying PIN."""
        r1 = self.setup_apn(apn)
        r2 = self.verify_pin(pin)
        ret = (r1 or r2)
        
        if ret is 0:
            self.configured = True

        return ret

    def get_wdm_device(self):
        """Put the device in correct USB mode by ejecting the mass storage device."""
        wdm_device = '/dev/cdc-wdm%s' %(self.iface.strip('wwan')) 
        try:
            subprocess.check_call('eject /dev/sr0', shell=True)
        except subprocess.CalledProcessError as err:
            logger.error('Could not switch to wdm device mode: %s' %(err))
            return 'None'
        
        logger.info('Switched to wdm device mode')
        
        return wdm_device

    def setup_apn(self, apn):
        """Setup the APN for internet connection by editing the '/etc/network/interfaces' file."""
        try:
            for line in FileInput('/etc/network/interfaces', inplace=1):
                if 'wwan_apn' in line:
                    line = '    wwan_apn "%s"\n' %(apn)
                print(line, end='')
        except FileNotFoundError as err:
            logger.error('Could not setup APN %s for "%s": %s' %(apn, self.iface, err))
            return 1
        
        self.apn = apn  
        logger.info('Setup APN %s for "%s"' %(apn, self.iface))

        return 0

    def qmi_network_ctrl(self, action):
        """Execute 'qmi-network' command with 'start' or 'stop' argument."""
        if action not in ['start', 'stop']:
            logger.error('Unknown action %s' %(action))
            return 1
        try:
            subprocess.check_call('/usr/bin/qmi-network %s %s' %(self.wdm_device, action), shell=True)
        except subprocess.CalledProcessError as err:
            logger.error('%s qmi-network failed: %s' %(action, err))
            return 1
        
        logger.info('%s qmi-network' %(action))

        return 0

    def verify_pin(self, pin):
        """Unlock the SIM card using the given PIN."""
        if self.wdm_device is None:
            logger.error('No wdm device present')
            return 1
        try:
            subprocess.check_call('/usr/bin/qmicli -d %s --dms-uim-verify-pin="PIN,%s"' %(self.wdm_device, pin), shell=True)
        except subprocess.CalledProcessError as err:
            logger.error('%s: pin verification failed: %s' %(self.iface, err))
            return 1
        
        logger.info('%s: pin verification successful' %(self.iface))
        self.pin = pin

        return 0

    def signal_strength(iface):
        """Return current signal strength of the wwan device."""
        signalStrength = 'None'
        wdm_device = '/dev/cdc-wdm0'
        try:
            out = subprocess.check_output('/usr/bin/qmicli -d %s --nas-get-signal-strength' %(wdm_device), shell=True).decode('utf-8')
        except subprocess.CalledProcessError as err:
            logger.error('%s: getting signal strength failed: %s' %(iface, err))
            return signalStrength
        
        if out is not None:
            for line in out.split('\n'):
                if 'Network' in line:
                    signalStrength = line.strip()

        return signalStrength
