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
    parser = argparse.ArgumentParser(prog='dlmclient', description='DLM Client main executable', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', metavar='<file>', default='/etc/dlmclient.json', help='configuration file for the DLM client')
    parser.add_argument('-v', metavar='<level>', choices=[0, 10, 20, 30, 40, 50], default=30, help='Logging level')
    parser.add_argument('-l', metavar='<file>', default='/var/log/dlmclient.log', help='log file location')
    parser.add_argument('--stats', action='store_true', default=False, help='print information about the DLM client')
    args = parser.parse_args()

    config = args.config
    loglevel = args.loglevel
    logfile = args.logfile
    stats = args.stats

    log.setup_logger('dlmclient', logfile, loglevel)
    dlmc = Dlmclient(configfile=config)

    # print status and config stats
    if stats is True:
        print_stats(dlmc)
        return 0

    # run dlmclient
    dlmc.configure_network()
    print('starting task scheduler')
    dlmc.schedule_events()
    sched_thread = dlmc.scheduler.get_run_thread()
    sched_thread.start()

    print('starting worker thread')
    dlmc.start_worker()

    while dlmc.worker.isAlive() or sched_thread.isAlive():
        time.sleep(1)
        pprint(dlmc.scheduler.queue)
        print('worker is active? :', dlmc.worker.isAlive())
        print('schedu is active? :', sched_thread.isAlive())

    print('Worker exited and all Tasks are done. Exit!')

    return 0

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(5)
    sys.exit(ret)        