from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import time

from .models import PaymentFile, Consumer
from concurrent.futures import ThreadPoolExecutor
from .processor import Processor

MAX_THREADS = 10


@receiver(post_save, sender=User)
def create_consumer(sender, instance, created, **kwargs):
    if created:
        Consumer.objects.create(user=instance)


@receiver(post_save, sender=PaymentFile)
def notified(sender, instance, created, **kwargs):
    if created:
        print('Notified: ', instance.file_name)
        proc = Processor()
        proc.daemon = True
        proc.start()
