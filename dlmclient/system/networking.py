from __future__ import print_function

import os.path
import subprocess
import logging
from fileinput import FileInput

logger = logging.getLogger('dlmclient')

def get_ip(iface):
    """Return the IP and netmask of the given interface."""
    ip = None
    netmask = None
    try:
        out = subprocess.check_output('ifconfig %s' %(iface), shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.error('Could not get ip address of interface "%s": %s' %(iface, err))    
        return (ip, netmask)
    
    config = out.split()
    ip = config[config.index('inet')+1]
    netmask = config[config.index('netmask')+1]
    logger.info('%s: IP address: %s, netmask: %s' %(iface, ip, netmask))

    return (ip,netmask)

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
        if not os.path.exists(wdm_device):
            logger.error('Could not switch to wdm device mode. Device %s does not exist' %(self.wdm_device))
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

    def signal_strength(self):
        """Return current signal strength of the wwan device."""
        signalStrength = 'None'
        if self.wdm_device is None:
            logger.error('No wdm device present')
            return 1

        try:
            out = subprocess.check_output('/usr/bin/qmicli -d %s --nas-get-signal-strength' %(self.wdm_device), shell=True).decode('utf-8')
        except subprocess.CalledProcessError as err:
            logger.error('%s: getting signal strength failed: %s' %(self.iface, err))
            return signalStrength
        
        if out is not None:
            for line in out.split('\n'):
                if 'Network' in line:
                    signalStrength = line.strip()

        return signalStrength
