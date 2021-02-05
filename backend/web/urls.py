from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.customers, name='customers'),
    path('staff-users', views.staff_users, name='staff-users'),
    path('file-entries', views.file_entries, name='file-entries'),
    path('payments', views.payments, name='payments'),
]
