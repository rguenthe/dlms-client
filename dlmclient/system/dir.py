import os.path
import logging

log = logging.getLogger('dlmclient')


def list_files(dir):
    """Return list of files in the given directory."""
    files = []
    if not os.path.exists(dir):
        log.error('directory "%s" does not exist!' % (dir))
        return files

    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
        break

    log.info('scanned files in dir "%s"' % (dir))
    return files
