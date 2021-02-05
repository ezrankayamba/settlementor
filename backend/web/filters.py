import django_filters
from core import models
from django import forms

STATUS_CHOICES = [
    ('', 'All'),
    ('Active', 'Active'),
    ('Pending', 'Pending'),
    ('Removed', 'Removed'),
    ('Initiated', 'Initiated'),
]

TRANS_STATUS_CHOICES = [
    ('', 'All'),
    ('Success', 'Success'),
    ('Fail', 'Fail'),
    ('Pending', 'Pending'),
]

BANK_CHOICES = [
    ('', 'All'),
    ('CRDB', 'CRDB'),
    ('EXIM', 'EXIM'),
    ('NMB', 'NMB'),
    ('NBC', 'NBC'),
]


ENTRY_TYPE_CHOICES = [
    ('', 'All'),
    ('PAYMENT_FILE', 'Payment File'),
]


class CustomerFilter(django_filters.FilterSet):
    owner_name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(
        widget=forms.Select(choices=STATUS_CHOICES),
    )

    class Meta:
        model = models.Customer
        fields = []


class PaymentFilter(django_filters.FilterSet):
    customer__owner_name = django_filters.CharFilter(widget=forms.Select(choices=[(x.owner_name, x.owner_name) for x in models.Customer.objects.all()]),)
    bank_id = django_filters.CharFilter(
        widget=forms.Select(choices=BANK_CHOICES),
    )
    status = django_filters.CharFilter(
        widget=forms.Select(choices=TRANS_STATUS_CHOICES),
    )

    class Meta:
        model = models.Payment
        fields = []


class FileEntryFilter(django_filters.FilterSet):
    file_name_in = django_filters.CharFilter(lookup_expr='icontains')
    entry_type = django_filters.CharFilter(
        widget=forms.Select(choices=ENTRY_TYPE_CHOICES),
    )
    status = django_filters.CharFilter(
        widget=forms.Select(choices=TRANS_STATUS_CHOICES),
    )

    class Meta:
        model = models.FileEntry
        fields = []
