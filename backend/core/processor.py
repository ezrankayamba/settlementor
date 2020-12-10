import time
import threading
import logging
from . import secure_files as sf
from . import secure_store as ss
from . import tta
from . import models
import csv

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
        with open(path) as csv_file:
            verified = sf.verify(path, self.file_entry.signature)
            print('Verified: ', verified)
            if verified:
                logger.debug('Successfully verified the signature. Continue with payment')
                username = consumer.tp_username
                # password = ss.retrieve('TELEPIN', username)
                bal_res, balance = tta.check_balance()
                if bal_res == 0:  # This has to be 0=Success
                    print('Success balance check')
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        company_id, amount, ref_number = row['CompanyID'], row['Amount'], row['ReferenceNumber']
                        print(company_id, amount, ref_number)
                        cust = models.Customer.objects.filter(owner_id=company_id).first()
                        if cust:
                            models.Payment.objects.create(customer=cust, reference_number=ref_number, bank_id=cust.bank_id, account_number=cust.account_number, consumer=consumer, amount=amount)
                            print('Recorded')
                        else:
                            print(f'Not found: {company_id}')
                    for payment in models.Payment.objects.filter(consumer=consumer, status='Pending'):
                        tta_res, trans_id = tta.pay_settlement(ref_number=ref_number, bank_account=cust.account_number,  amount=amount)
                        payment.status = 'Success' if tta_res == 0 else 'Submitted' if tta_res == 99999 else 'Fail'
                        payment.result_code = tta_res
                        payment.trans_id = trans_id
                        payment.save()
                else:
                    print(balance)
            else:
                logger.debug(f'Signature is not valid: {self.file_entry.file_name}')
