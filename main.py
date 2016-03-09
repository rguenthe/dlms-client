import sys
import argparse
import logging
import time

import dlmclient

logger = dlmclient.log.setup_logger('dlmclient', '.dlmclient.log', logging.DEBUG)
logger = logging.getLogger('dlmclient')

def main():
    parser = argparse.ArgumentParser(description='DLM-Client: Datalogger Management Client. Communicates with the DLM webservice and controls data logging application')
    parser.add_argument('config_file', help='File containing the configuration for the DLM client')
    args = parser.parse_args()

    config_file = args.config_file

    dlmc = dlmclient.Dlmclient(configfile=config_file)

    dlmc.download_config()

    #status_ev,config_ev = dlmc.schedule_tasks()
    #print('starting task scheduler')
    #sched_thread = dlmc.scheduler.get_run_thread()
    #sched_thread.start()
    #print('starting worker thread')
    #dlmc.start_worker()

    #while (dlmc.worker.isAlive() or sched_thread.isAlive()):
    #    time.sleep(1)
    #    print(dlmc.scheduler.queue)

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