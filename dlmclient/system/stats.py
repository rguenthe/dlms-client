import subprocess
import re
import logging

log = logging.getLogger('dlmclient')


def uptime():
    """Return the output of the 'uptime' command."""
    cmd = 'uptime'
    try:
        out = subprocess.check_output('uptime', shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        log.error('Error reading uptime: %s' %(err))
        return 'None'

    uptime = re.sub(' +', ' ', out.strip())
    log.info('read uptime')

    return uptime


def disk_usage(device):
    """Return disk usage information for the given storrage device."""
    disk_usage = 'None'
    cmd = 'df -h | grep -E "%s"' %(device)
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        log.error('Error reading disk usage: %s' %(err))
        return 'None'
    
    disk_usage = re.sub(' +', ' ', out.strip())
    log.info('read disk_usage')
    
    return disk_usage


def mem_info():
    """Return memory information."""
    cmd = 'free | grep -E "Mem|total"'
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        log.error('Error reading memory information: %s' %(err))
        return 'None'
    
    out = out.split('\n')
    keys = out[0].split()
    values = out[1].strip('Mem:').split()
    mem_info = dict(zip(keys, values))
    log.info('read mem info')
    
    return mem_info