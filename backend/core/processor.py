import time
import threading
import logging

logger = logging.getLogger(__name__)


class Processor(threading.Thread):
    def __init__(self, file_entry, **kwargs):
        super(Processor, self).__init__(**kwargs)
        self.file_entry = file_entry

    def run(self):
        time.sleep(10)
        logger.debug(f'Done processing the file ...{ self.file_entry}')
