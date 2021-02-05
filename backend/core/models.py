from django.db import models
from django.contrib.auth.models import User


class Consumer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    status = models.CharField(default='Active', max_length=10)
    tp_username = models.CharField(max_length=20, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f'{self.user.username}({self.status})'


class Customer(models.Model):
    owner_id = models.CharField(unique=True, max_length=20)
    recorded_at = models.DateTimeField(auto_now_add=True)
    owner_name = models.CharField(max_length=100)
    bank_id = models.CharField(max_length=10)
    bank_id_req = models.CharField(max_length=10, null=True)
    account_number = models.CharField(max_length=20)
    account_number_req = models.CharField(max_length=20, null=True)
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='Pending')
    command = models.CharField(max_length=20)
    request = models.CharField(max_length=20)
    approval_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return f'{self.owner_id} - {self.owner_name}|{self.bank_id}/{self.account_number}|{self.status}'
        return self.owner_name


class FileEntry(models.Model):
    file_name_in = models.CharField(max_length=20, unique=True)
    file_name_out = models.CharField(max_length=20, unique=True, null=True)
    timestamp = models.CharField(max_length=40)
    file_reference_id = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=40)
    count_of_records = models.IntegerField()
    status = models.CharField(max_length=20, default='Pending')
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
    entry_type = models.CharField(max_length=20, default='PAYMENT_FILE')
    signature = models.CharField(max_length=1000, null=True)

    class Meta:
        verbose_name_plural = 'File entries'


class Payment(models.Model):
    reference_number = models.CharField(max_length=20)
    file_entry = models.ForeignKey(FileEntry, null=True, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    bank_id = models.CharField(max_length=10)
    account_number = models.CharField(max_length=20)
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    status = models.CharField(max_length=20, default='Pending')
    result_code = models.CharField(max_length=20, null=True)
    trans_id = models.CharField(max_length=50, null=True)

    class Meta:
        unique_together = ['reference_number', 'consumer']
