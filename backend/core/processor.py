import time
import threading
import logging

logger = logging.getLogger(__name__)


class Processor(threading.Thread):
    def __init__(self,  **kwargs):
        super(Processor, self).__init__(**kwargs)

    def run(self):
        time.sleep(10)
        logger.debug('Done processing the file ...')
