import sys
import argparse
import logging

import dlmclient

logger = dlmclient.log.setup_logger('dlmclient', '.dlmclient.log', logging.DEBUG)
logger = logging.getLogger('dlmclient')

def main():
    parser = argparse.ArgumentParser(description='DLM-Client: Datalogger Management Client. Communicates with the DLM webservice and controls data logging application')
    parser.add_argument('config_file', help='File containing the configuration for the DLM client')
    args = parser.parse_args()

    config_file = args.config_file

    dlmc = dlmclient.Dlmclient(configfile=config_file)
    dlmc.config.read_xml('testfiles/config.xml')
    dlmc.webinterface.upload_status('testfiles/statusx.xml')
    dlmc.webinterface.upload_dataset('testfiles/config.xml')
    dlmc.webinterface.download_config('testfiles/new_config.xml')
    print(dlmclient.system.networking.wait_for_ip('wlp3s0', 10))

    return 0

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(5)
    sys.exit(ret)        