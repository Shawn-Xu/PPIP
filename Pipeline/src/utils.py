import logging
import os
import time
import shutil

logger = logging.getLogger(__name__)

def create_dirs(dirlist):
    for dirname in dirlist:
        if not os.path.isdir(dirname):
            logger.info("Creating directory %s" % (dirname))
            os.makedirs(dirname)

def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)
    else:
        shutil.copytree(from_path, to_path)

class chainMap(list):
    def __init__(self, l):
        list.__init__(self,l)
    def map(self, f):
        return ChainMap(map(f, self[:]))
