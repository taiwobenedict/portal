import pytz
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

User = settings.AUTH_USER_MODEL


class CallbackRechargeAirtimeAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    callback_success_code = models.CharField(max_length=500, default='ORDER_COMPLETED')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Airtime Recharge Callback'
        verbose_name_plural = 'APIs For Airtime Recharge Callbacks'

class CallbackDataNetworksApi(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    callback_success_code = models.CharField(max_length=500, default='ORDER_COMPLETED')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Data Recharge Callback'
        verbose_name_plural = 'APIs For Data Recharge Callbacks'

class CallbackCableRecharegAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    callback_success_code = models.CharField(max_length=500, default='ORDER_COMPLETED')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Cable Callback'
        verbose_name_plural = 'API For Cable Callbacks'

class CallbackElectricityAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    callback_success_code = models.CharField(max_length=500, default='ORDER_COMPLETED')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Cable Callback'
        verbose_name_plural = 'API For Cable Callbacks'
