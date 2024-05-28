from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class ApiKeyActivation(models.Model):
    user = models.OneToOneField(User, related_name='user_apikeyactivation', on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    domain = models.CharField(max_length=200, blank="", null=True)
    api_user = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

class KycApi(models.Model):
    CHOICES = (
        ("BVN", "BVN"),
        ("NIN", "NIN")
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    url_data = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    sms_url = models.TextField(blank=True, null=True)
    sms_url_data = models.TextField(blank=True, null=True)
    sms_success_code = models.TextField(blank=True, null=True)
    success_code = models.CharField(max_length=200, blank=True, null=True)
    kyc_cost = models.FloatField(default=0.0)
    kyc_type = models.CharField(max_length=20, default="BVN", choices=CHOICES)
    do_verifcation = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name