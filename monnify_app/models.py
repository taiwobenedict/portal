from django.db import models
from smsangosend.models import *

class MonnifyKeys(models.Model):
    apiKey = models.CharField(max_length=200, default='')
    clientSecret = models.CharField(max_length=200, default='')
    currencyCode = models.CharField(max_length=10, default='NGN')
    contractCode = models.CharField(max_length=200, default='')
    fee = models.FloatField(default=0.0, help_text='percentage amount to deduct from the transferred amount e.g 0.9% means 0.009')
    maxAmountToDeductFee = models.FloatField(default=0.0, help_text="maximum amount by which the fee above will apply")
    maxAmountFeeToDeduct = models.FloatField(default=0.0, help_text="The maximum fee to deduct when the maximum amount is exceeded")
    source_account_number = models.CharField(max_length=200, default='99999', blank=True, null=True)

    monnify_card_fee = models.FloatField(default=0.0, help_text="this is the fee ravepay charges in percentage so 0.09 means 9% of the funds to be paid")
    monnify_card_funding_limit = models.IntegerField(default=5000)

    def __str__(self):
        return 'Monnify Api Details'

    def __unicode__(self):
        return 'Monnify Api Details'


class MonnifyAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_monnify_acc")
    accountReference = models.CharField(max_length=50, default='', unique=True)
    accountNumber = models.CharField(max_length=500, default='')
    currencyCode = models.CharField(max_length=50, default='')
    contractCode = models.CharField(max_length=50, default='')
    accountName = models.CharField(max_length=500, default='')
    customerEmail = models.CharField(max_length=50, default='')
    bankName = models.CharField(max_length=500, default='')
    bankCode = models.CharField(max_length=500, default='')
    reservationReference = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    createdOn = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.accountNumber)+ '-' +str(self.user.username)

    def __unicode__(self):
        return str(self.accountNumber)+ '-' +str(self.user.username)

