import time
import threading
import logging
from . import secure_files as sf
from . import secure_store as ss
from . import tta

logger = logging.getLogger(__name__)


class Processor(threading.Thread):
    def __init__(self, file_entry, **kwargs):
        super(Processor, self).__init__(**kwargs)
        self.file_entry = file_entry

    def run(self):
        time.sleep(2)
        consumer = self.file_entry.consumer
        logger.debug(f'{consumer.msisdn} = {self.file_entry.file_name}')
        logger.debug(f'Signature: { self.file_entry.signature}')
        path = f'files/{self.file_entry.file_name}'
        with open(path) as f:
            verified = sf.verify(path, self.file_entry.signature)
            print('Verified: ', verified)
            if verified:
                logger.debug('Successfully verified the signature. Continue with payment')
                username = consumer.msisdn
                password = ss.retrieve('TELEPIN', username)
                tta.check_balance(username, password)
            else:
                logger.debug(f'Signature is not valid: {self.file_entry.file_name}')
