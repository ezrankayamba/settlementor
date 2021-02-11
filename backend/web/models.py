from django.db import models
from django.contrib.auth.models import User


class TwoFactorAuth(models.Model):
    otp = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.DurationField()
    status = models.IntegerField(default=0)
