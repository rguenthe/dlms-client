import sys
import argparse
import time

from pprint import pprint

from dlmclient.dlmclient import Dlmclient
from dlmclient.status import Status
from dlmclient import log


def print_stats(dlmc):
    print('\nDLM Client stats:')
    print('-------------------------------------------------------')

    status = Status(dlmc.config)
    print('\nStatus:')
    pprint(status.status)

    print('\nConfiguration:')
    pprint(dlmc.config.dict)
    print('\n')

    return 0


def main():
    """
    Datalogger Management Client (DLMC) main executable
    """

    # argument parsing
    parser = argparse.ArgumentParser(prog='dlmclient',
                                     description='DLM Client main executable',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', metavar='<configfile>', default='/etc/dlmclient.json', help='configuration file for the DLM client')
    parser.add_argument('-v', metavar='<loglevel>', choices=[0, 10, 20, 30, 40, 50], default=30, help='Logging level')
    parser.add_argument('-l', metavar='<logfile>', default='/var/log/dlmclient.log', help='log file location')
    parser.add_argument('--stats', action='store_true', default=False, help='print information about the DLM client')
    args = parser.parse_args()

    configfile = args.c
    loglevel = args.v
    logfile = args.l
    stats = args.stats

    log.setup_logger('dlmclient', logfile, loglevel)
    dlmc = Dlmclient(configfile=configfile)

    # print status and config stats
    if stats is True:
        print_stats(dlmc)
        return 0

    # -----------------------------------------------------------------------------------------------------------------
    print('----------------------------------------')
    print('DLM Client')
    print('----------------------------------------\n')

    print('Initialize:')
    print('  configure network access')
    dlmc.configure_network()
    dlmc.vpn_network.connect()

    print('  downloading configuration from server')
    dlmc.download_config()

    print('  uploading status to server')
    dlmc.upload_status()

    dlmc.vpn_network.connect()

    print('Run:')
    print('  scheduling tasks')
    dlmc.schedule_events()
    st = dlmc.scheduler.get_run_thread()
    st.start()

    print('  starting worker thread')
    dlmc.worker_start()
    while dlmc.worker.isAlive():
        time.sleep(5)

    print('  starting postprocessing thread')
    dlmc.postprocessor_start()
    while dlmc.postprocessor.isAlive():
        time.sleep(5)

    dlmc.upload_dataset()

    print('done')

    # -----------------------------------------------------------------------------------------------------------------

    return 0

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(5)
    sys.exit(ret)        