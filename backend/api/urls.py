from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('fileshared', views.PaymentFileSharedView.as_view()),
    path('whitelist', views.WhitelistView.as_view()),
    path('approval', views.WhiteListApprovalView.as_view()),
]
