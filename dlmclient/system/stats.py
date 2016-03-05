from __future__ import print_function

import sys
import subprocess
import re
import logging

logger = logging.getLogger('dlmclient')

def uptime():
    """Return the output of the 'uptime' command."""
    cmd = 'uptime'
    try:
        out = subprocess.check_output('uptime', shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.error('Error reading uptime: Could ne execute "%s": %s' %(cmd, err))
        return 'None'

    uptime = re.sub(' +', ' ', out.strip())
    logger.info('read uptime')

    return uptime

def disk_usage(device):
    """Return disk usage information for the given storrage device."""
    disk_usage = 'None'
    cmd = 'df | grep -E "%s"' %(device)
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.error('Error reading disk usage: Could ne execute "%s": %s' %(cmd, err))
        return 'None'
    
    disk_usage = re.sub(' +', ' ', out.strip())
    logger.info('read disk_usage')
    
    return disk_usage

def mem_info():
    """Return memory information."""
    cmd = 'free | grep -E "Mem|total"'
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.error('Error reading memory information: Could ne execute "%s"' %(cmd))
        return 'None'
    
    out = out.split('\n')
    keys = out[0].split()
    values = out[1].strip('Mem:').split()
    mem_info = dict(zip(keys, values))
    logger.info('read mem info')
    
    return mem_info