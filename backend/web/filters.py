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


class CustomerFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        widget=forms.Select(choices=STATUS_CHOICES),
    )

    class Meta:
        model = models.Customer
        fields = ['owner_name']
