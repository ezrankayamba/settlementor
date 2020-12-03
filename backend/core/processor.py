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
        consumer = self.file_entry.consumer
        logger.debug(f'{consumer.msisdn} = {self.file_entry.file_name}')
        logger.debug(f'Done processing the file ...{ self.file_entry}')
        with open(f'files/{self.file_entry.file_name}') as f:
            print('File read!')
