import json
import logging
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from .models import FileEntry, Consumer, Customer, Payment
from .processor import Processor
from .notification import send_message
from datetime import datetime
from config import config as cfg
from core import secure_files as sf
from core import sftp_connect as sftp
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

MAX_THREADS = 10


def sanitize_id(c_id):
    id_str = str(c_id)
    new_id = id_str.split('_')[0]
    return new_id


@receiver(post_save, sender=User)
def create_consumer(sender, instance, created, **kwargs):
    logger.debug(f'User created/updated: {instance}')
    if created:
        Consumer.objects.create(user=instance)


@receiver(post_save, sender=FileEntry)
def notified_file_entry(sender, instance, created, **kwargs):
    logger.debug("FileEntry created/updated: %s", instance)
    if created:
        logger.debug(f'Notified: {instance}')
        proc = Processor(instance)
        proc.daemon = True
        proc.start()
    else:
        def run():
            logger.debug('FileEntry updated: %s', instance)
            try:
                remote_path = cfg.sftp_tigo_path()
                sftp.upload(instance.file_name_out, remote_path)
                sig = sf.sign(f'{cfg.sftp_local_path()}/{instance.file_name_out}', '2020')
                headers = {'Content-Type': 'application/json'}
                total = 0
                count = 0
                for payment in Payment.objects.filter(consumer=instance.consumer, reference_number=instance.file_reference_id, status='Success'):
                    total += payment.amount
                    count += 1

                data = {
                    "fileName": instance.file_name_out,
                    "timestamp": datetime.now().isoformat(timespec='minutes'),
                    "fileReferenceId": instance.file_reference_id,
                    "totalAmountPaid": total,
                    "countOfRecordsPaid": count,
                    "fileSignature": sig
                }
                logger.debug(data)
                res = requests.post(cfg.result_file_url(), json=data, headers=headers)
                if res.ok:
                    logger.info('Callback result: %s', res.text)
                else:
                    logger.error('Fail callback result: %s', res.text)
            except Exception as ex:
                logger.error("Error processing Result file sending: %s", ex)
        t = threading.Thread(target=run)
        t.start()


@receiver(post_save, sender=Customer)
def notified_customer_update(sender, instance, created, **kwargs):
    def run():
        logger.debug(f'FileEntry created/updated: {instance}')
        try:
            if instance.request == 'Initiated':
                logger.debug(f'Initiated: {instance}')
                try:
                    msg = f'Customer Whitelist Approval:\nRequested action: {instance.command}\nOwner Name: {instance}. \n\nRegards,\nSettlementor'
                    send_message(message=msg, receiver='255713123066')
                except Exception as ex:
                    logger.error(f'Error sending SMS: {ex}')

                try:
                    msg = f'<h3>Customer Whitelist Approval</h3><label>Requested action:</label> {instance.command}<br/><label>Owner Name:</label> {instance}.<br/><br/>Regards,<br/>Settlementor'
                    send_message(message=msg, receiver='godfred.nkayamba@tigo.co.tz', channel='Email', email_sub='WL Approval')
                except Exception as ex:
                    logger.error(f'Error sending mail: {ex}')

            else:
                logger.debug(f'Approval: {instance}')
                data = {
                    "companyID": sanitize_id(instance.owner_id),
                    "approval": instance.request,
                    "command": instance.command,
                    "timestamp": datetime.now().isoformat(timespec='minutes')
                }
                url = cfg.approval_url()
                logger.debug(f'Url: {url}')
                logger.debug(f'Data: {data}')

                headers = {'Content-Type': 'application/json'}
                res = requests.post(url, data=json.dumps(data), headers=headers)
                logger.info(f'Response: {res.text}')
        except Exception as ex:
            logger.error(f'Error: {ex}')
    t = threading.Thread(target=run)
    t.start()
