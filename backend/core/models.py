from django.db import models
from django.contrib.auth.models import User


class Consumer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    status = models.CharField(default='Active', max_length=10)


class Customer(models.Model):
    owner_id = models.CharField(unique=True, max_length=20)
    owner_name = models.CharField(max_length=100)
    bank_id = models.CharField(max_length=10)
    account_number = models.CharField(max_length=20)
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)


class Payment(models.Model):
    reference_number = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    bank_id = models.CharField(max_length=10)
    account_number = models.CharField(max_length=20)
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    status = models.CharField(max_length=20, default='Pending')
    result_code = models.CharField(max_length=20, null=True)

    class Meta:
        unique_together = ['reference_number', 'consumer']


class PaymentFile(models.Model):
    file_name = models.CharField(max_length=20, unique=True)
    timestamp = models.CharField(max_length=40)
    file_reference_id = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=40)
    count_of_records = models.IntegerField()
    status = models.CharField(max_length=20, default='Pending')
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
