from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from .models import FileEntry, Consumer, Customer
from .processor import Processor
from .notification import send_message
import threading
import requests
from datetime import datetime
from config import config as cfg

logger = logging.getLogger(__name__)

MAX_THREADS = 10


@receiver(post_save, sender=User)
def create_consumer(sender, instance, created, **kwargs):
    logger.debug(f'User created/updated: {instance}')
    if created:
        Consumer.objects.create(user=instance)


@receiver(post_save, sender=FileEntry)
def notified_file_entry(sender, instance, created, **kwargs):
    logger.debug(f'FileEntry created/updated: {instance}')
    if created:
        print('Notified: ', instance.file_name)
        proc = Processor(instance)
        proc.daemon = True
        proc.start()


@receiver(post_save, sender=Customer)
def notified_customer_update(sender, instance, created, **kwargs):
    def run():
        logger.debug(f'FileEntry created/updated: {instance}')
        try:
            if instance.request == 'Initiated':
                logger.debug(f'Initiated: {instance}')
                msg = f'Approve {instance.command} of customer. \nDetails: {instance}'
                try:
                    send_message(message=msg, receiver='255713123066')
                except Exception as ex:
                    logger.error(f'Error: {ex}')

                try:
                    send_message(message=msg, receiver='godfred.nkayamba@tigo.co.tz', channel='Email', email_sub='WL Approval')
                except Exception as ex:
                    logger.error(f'Error: {ex}')

            else:
                logger.debug(f'Approval: {instance}')
                data = {
                    "companyID": instance.owner_id,
                    "approval": instance.request,
                    "command": instance.command,
                    "timestamp": datetime.now().isoformat(timespec='minutes')
                }
                url = cfg.approval_url()
                logger.debug(f'Url: {url}')
                logger.debug(f'Data: {data}')
                requests.post(url, data=data)
        except Exception as ex:
            logger.error(f'Error: {ex}')
    t = threading.Thread(target=run)
    t.start()
