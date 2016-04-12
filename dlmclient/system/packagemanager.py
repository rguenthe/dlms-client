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


def run_maintenance(pkgfile):
    """Do package maintenance by """
    if not os.path.exists(pkgfile):
        log.error('could not update configuration: File "%s" does not exists' %(pkgfile))
        return 1

    with open(pkgfile, 'r') as fp:
        pkg_maintenance_data = json.load(fp)
        fp.close()

    # update package list
    update()

    # install / upgrade packages from the file
    for package in pkg_maintenance_data['upgrade']:
        install_or_upgrade(package)

    return 0