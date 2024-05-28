from django.conf import settings
from django.db.models import Q
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse

User = settings.AUTH_USER_MODEL

# Create your models here.

class PricingPerSMSPerUserToPurchase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='smspricingperuser')
    price = models.FloatField(default=1.0, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Pricing Per Credit Per User To Purchase'
        verbose_name_plural = 'Pricing Per Credit Per User To Purchase'

class DefaultPricePerSMSToPurchase(models.Model):
    priceperunit = models.DecimalField(null=True, blank=False, default=1.0, max_digits=10, decimal_places=2)
    lowprice = models.PositiveIntegerField(null=True, blank=False, default=1)
    highprice = models.PositiveIntegerField(null=True, blank=False, default=9999)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.lowprice) + '-' + str(self.highprice)

    class Meta:
        verbose_name = 'Default Price Per Credit To Purchase'
        verbose_name_plural = 'Default Price Per Credit To Purchase'

class BonusesPercentage(models.Model):
    bonus_name = models.CharField(default='', max_length=30)
    purchase_airtime_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    purchase_data_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    purchase_cable_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    purchase_electricity_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    education_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    spectranet_bonus = models.TextField(default='{"spectranet_bonus": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    smile_bonus = models.TextField(default='{"smile_bonus": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_airtime_bonus = models.TextField(default='{"identifier": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_data_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_cable_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_electricity_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_pin_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_bonus = models.FloatField(default=0.0, blank=True, null=True, help_text="Referral is not in percentage but actual value e.g 400.0 etc it used for giving signup bonuses to A who referred B when B signs up")
    referral_education_bonus = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_smile_bonus = models.TextField(default='{"smile_bonus": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_spectranet_bonus = models.TextField(default='{"spectranet_bonus": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_activation_reseller_bonus = models.TextField(default='{"reseller_plan_name": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    referral_upgrade_reseller_bonus = models.TextField(default='{"reseller_plan_name": 0.01}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
    signup_bonus = models.FloatField(default=0.0, blank=True, null=True, help_text="amount given to a user when they sign up actual values e.g 200")
    is_active = models.BooleanField(default=False)
    def __str__(self):
        return self.bonus_name