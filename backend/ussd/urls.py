from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('menus/', views.menus),
    path('', views.ussd_home, name='ussd-home'),
]
