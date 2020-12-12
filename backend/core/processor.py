import time
import threading
import logging
from . import secure_files as sf
from . import secure_store as ss
from . import tta
from . import models
import pandas as pd
import csv
from . import sftp_connect as sftp
from config import config as cfg

logger = logging.getLogger(__name__)


class Processor(threading.Thread):
    def __init__(self, file_entry, **kwargs):
        super(Processor, self).__init__(**kwargs)
        self.file_entry = file_entry

    def run(self):
        try:
            if not sftp.download(cfg.sftp_tapsoa_path(), self.file_entry.file_name):
                raise Exception('Failure on downloading file')

            consumer = self.file_entry.consumer
            logger.debug(f'{consumer.tp_username} = {self.file_entry.file_name}')
            logger.debug(f'Signature: { self.file_entry.signature}')
            path = f'files/{self.file_entry.file_name}'
            with open(path) as csv_file:
                verified = sf.verify(path, self.file_entry.signature)
                logger.debug(f'Verified:  {verified}')
                if verified:
                    logger.debug('Successfully verified the signature. Continue with payment')
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        company_id, amount, ref_number = row['CompanyID'], row['Amount'], row['ReferenceNumber']
                        logger.debug(f'{company_id}, {amount}, {ref_number}')
                        cust = models.Customer.objects.filter(owner_id=company_id).first()
                        if cust:
                            models.Payment.objects.create(file_entry=self.file_entry, customer=cust, reference_number=ref_number,
                                                          bank_id=cust.bank_id, account_number=cust.account_number, consumer=consumer, amount=amount)
                        else:
                            logger.error(f'Not found: {company_id}')
                    for payment in models.Payment.objects.filter(consumer=consumer, status='Pending'):
                        tta_res, trans_id = tta.pay_settlement(ref_number=ref_number, bank_account=cust.account_number,  amount=amount)
                        payment.status = 'Success' if tta_res == 0 else 'Submitted' if tta_res == 99999 else 'Fail'
                        payment.result_code = tta_res
                        payment.trans_id = trans_id
                        payment.save()
                    payments = models.Payment.objects.filter(file_entry=self.file_entry)
                    df2 = pd.DataFrame.from_records(payments.values_list('reference_number',  'status', 'result_code', 'trans_id'), columns=['reference_number',  'status', 'result_code', 'trans_id'])
                    df2.rename(columns={'reference_number': 'ReferenceNumber', 'status': 'Status', 'result_code': 'ResultCode', 'trans_id': 'TransID'}, inplace=True)
                    logger.debug(df2.head(2))
                    df1 = pd.read_csv(f'{cfg.sftp_local_path()}/{self.file_entry.file_name}')
                    logger.debug(df1.head(2))
                    df = pd.merge(df1, df2[["Status", "ResultCode", "TransID"]], on='ReferenceNumber', how='left')
                    file_name = f'Payment_Result_File_{self.file_entry.file_reference_id}.csv'
                    local_path = cfg.sftp_local_path()
                    remote_path = cfg.sftp_tigo_path()
                    df.to_csv(f'{local_path}/{file_name}.csv', index=False)
                    sftp.upload(remote_path, file_name)

                    file_entry = self.file_entry
                    file_entry.status = 'Processed'
                else:
                    logger.debug(f'Signature is not valid: {self.file_entry.file_name}')
        except Exception as ex:
            logger.error(f"Error processing: {ex}")
