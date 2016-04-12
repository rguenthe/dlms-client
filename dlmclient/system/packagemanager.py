import subprocess
import logging
import json
import os

log = logging.getLogger('dlmclient')


def install_or_upgrade(package=''):
    """install the given package."""
    cmd = 'opkg install %s' %(package)
    try:
        ret = subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as err:
        log.error('error installing package: "%s":%s' %(package, err))
        ret = 1

    return ret


def update():
    """install the given package."""
    cmd = 'opkg update'
    try:
        ret = subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as err:
        log.error('error updating package list: :%s' %(err))
        ret = 1

    return ret


def run_maintenance(upgrade_packages):
    """Do package maintenance by """
    # update package list
    update()

    # install / upgrade packages from the file
    for pkg in upgrade_packages:
        install_or_upgrade(pkg)

    return 0