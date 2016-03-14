import sys
import argparse
import time

from pprint import pprint

from dlmclient.dlmclient import Dlmclient
from dlmclient import log


def main():
    """
    Datalogger Management Client (DLMC) main executable
    """

    parser = argparse.ArgumentParser(prog='dlmclient', description='DLM Client main executable')
    parser.add_argument('-c', '--config', default='/etc/dlmconfig.json', help='File containing the configuration for the DLM client')
    parser.add_argument('-l', '--loglevel', default=30, help='Logging level (default: 30)')
    parser.add_argument('-f', '--logfile', default='/var/log/dlmclient.log', help='log file location (default: /var/log/dlmclient.log)')
    args = parser.parse_args()

    config = args.config
    loglevel = args.loglevel
    logfile = args.logfile

    log.setup_logger('dlmclient', logfile, loglevel)
    dlmc = Dlmclient(configfile=config)

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