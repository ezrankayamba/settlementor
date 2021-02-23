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
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class Processor(threading.Thread):
    def __init__(self, file_entry, **kwargs):
        super(Processor, self).__init__(**kwargs)
        self.file_entry = file_entry

    def run(self):
        try:
            if not sftp.download(cfg.sftp_tapsoa_path(), self.file_entry.file_name_in):
                raise Exception('Failure on downloading file')

            consumer = self.file_entry.consumer
            logger.debug(f'{consumer.tp_username} = {self.file_entry.file_name_in}')
            logger.debug(f'Signature: { self.file_entry.signature}')
            path = f'files/{self.file_entry.file_name_in}'
            with open(path) as csv_file:
                verified = sf.verify(path, self.file_entry.signature)
                logger.debug(f'Verified:  {verified}')
                df1 = pd.read_csv(path)
                logger.debug(df1.head(2))
                if verified:
                    logger.debug('Successfully verified the signature. Continue with payment')
                    reader = csv.DictReader(csv_file)
                    headers = reader.fieldnames
                    logger.debug(headers)
                    required_cols = ['CompanyID', 'Amount', 'ReferenceNumber']
                    logger.debug(required_cols)
                    if set(required_cols).issubset(set(headers)):
                        for row in reader:
                            try:
                                company_id, amount, ref_number = row['CompanyID'], row['Amount'], row['ReferenceNumber']
                                logger.debug(f'{company_id}, {amount}, {ref_number}')
                                cust = models.Customer.objects.filter(owner_id=company_id, status='Active').first()
                                if cust:
                                    models.Payment.objects.create(file_entry=self.file_entry, customer=cust, reference_number=ref_number,
                                                                  bank_id=cust.bank_id, account_number=cust.account_number, consumer=consumer, amount=amount)
                                else:
                                    logger.error(f'Not found: {company_id}')
                            except Exception as ex:
                                logger.error(f'Error recording payment: {ex}')

                        total = 0
                        count = 0
                        for payment in models.Payment.objects.filter(consumer=consumer, status='Pending'):
                            try:
                                tta_res, trans_id = tta.pay_settlement(ref_number=payment.reference_number, bank_account=payment.account_number,  amount=amount, bank_id=payment.bank_id)
                                payment.status = 'Success' if tta_res == 0 else 'Submitted' if tta_res == 99999 else 'Fail'
                                payment.result_code = tta_res
                                payment.trans_id = trans_id
                                payment.save()
                                if payment.status == 'Success':
                                    total += payment.amount
                                    count += 1
                            except Exception as ex:
                                logger.error(f"Error doing payment for {payment.ref_number}")

                        payments = models.Payment.objects.filter(file_entry=self.file_entry)
                        df2 = pd.DataFrame.from_records(payments.values_list('reference_number',  'status', 'result_code', 'trans_id'),
                                                        columns=['reference_number',  'status', 'result_code', 'trans_id'])
                        df2.rename(columns={'reference_number': 'ReferenceNumber', 'status': 'Status', 'result_code': 'ResultCode', 'trans_id': 'TransID'}, inplace=True)
                        logger.debug(df2.head(2))
                        df = pd.merge(df1, df2[["ReferenceNumber", "Status", "ResultCode", "TransID"]], on='ReferenceNumber', how='left')
                        df['Remarks'] = 'Processed'
                    else:
                        logger.debug(f'File format is not valid: {self.file_entry.file_name_in}')
                        df1['ReferenceNumber'] = None
                        df1['Status'] = 'Fail'
                        df1['ResultCode'] = -99
                        df1['TransID'] = None
                        df1['Remarks'] = 'Invalid file format'
                        df = df1
                else:
                    logger.debug(f'Signature is not valid: {self.file_entry.file_name_in}')
                    df1['ReferenceNumber'] = None
                    df1['Status'] = 'Fail'
                    df1['ResultCode'] = -99
                    df1['TransID'] = None
                    df1['Remarks'] = 'Invalid signature'
                    df = df1

                file_name = f'Payment_Result_File_{self.file_entry.file_reference_id}.csv'
                local_path = cfg.sftp_local_path()
                res_file = f'{local_path}/{file_name}'
                df.to_csv(res_file, index=False)

                file_entry = self.file_entry
                file_entry.status = 'Processed'
                file_entry.file_name_out = file_name
                file_entry.save()

        except Exception as ex:
            logger.error(f"Error processing: {ex}")
