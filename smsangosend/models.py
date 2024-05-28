from django.utils.safestring import mark_safe
from user_transactions.models import AllUserTransactionsLogs
from django.conf import settings
from django.db.models import Q
from django.db import models
from django.db.models.signals import pre_save, post_save, post_migrate
from django.dispatch import receiver
from django.core.mail import send_mail

from django.contrib.auth.models import User
from django.urls import reverse
import datetime
import pytz
from smsangonumcredit.models import PricingPerSMSPerUserToPurchase
from rechargeapp.models import BonusAccount, RefBonusAccount
utc=pytz.UTC

from coreconfig.models import DashboardConfig
from rest_framework.authtoken.models import Token

# Create your models here.
User = settings.AUTH_USER_MODEL

class SmsangoSendSMS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smsangosendsms')
    reference = models.CharField(max_length=30, blank=True, null=True)
    sender = models.CharField(max_length=11)
    recipients = models.TextField(help_text='Seperate each Items by comma', null=False, blank=False)
    messagecontent = models.TextField(null=False, blank=False)
    notsently = models.TextField(null=True, blank= True)
    sently = models.TextField(null=True, blank= True)
    apiRoute = models.CharField(max_length=15, default="NON DND ROUTE")
    status = models.CharField(max_length=200)
    creditusedall = models.CharField(max_length=10, default='')
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    numcount = models.IntegerField(default=0, blank=True, null=True)
    smsroute = models.TextField(null=True, blank= True)
    totalsms = models.CharField(max_length=500, default='')
    pages = models.CharField(max_length=500, default='')
    scheduledsms = models.BooleanField(default=False)
    time_to_send = models.DateTimeField(null=True, blank=True)
    scheduleidnum = models.CharField(max_length=15, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender


@receiver(post_save, sender=SmsangoSendSMS)
def sendsms_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = "send sms",
        trans_id = obj.reference,
        status = obj.status,
        amount = obj.old_balance - obj.new_balance,
        log = f"Send SMS: {obj.user.username} attempted to send sms at {obj.timestamp} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )


class SavedScheduledSMS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savedschedulesendsms')
    sender = models.CharField(max_length=11)
    recipients = models.TextField(help_text='Seperate each Items by comma', null=False, blank=False)
    messagecontent = models.TextField(null=False, blank=False)
    smsroute = models.CharField(max_length=10, default='')
    time_to_send = models.DateTimeField()
    status = models.BooleanField(default=False)
    scheduleidnum = models.CharField(max_length=15, default='')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender + ' ' + self.user.username
    
    class Meta:
        verbose_name = 'Saved Scheduled SMS'
        verbose_name_plural = 'Saved Scheduled SMS'



class PhoneBookContacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phonebook')
    name_contacts = models.CharField(max_length=20, default='')
    contact_numbers = models.TextField(max_length=6000, default='')
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name_contacts
    def GetEachCountOfStoreNumber(self):
        phk = self.contact_numbers
        print(phk)
        phkk = phk.split(',')
        totalphk = len(phkk)
        return totalphk

class SmsangoSBulkCredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='smsbulkcredit')
    smscredit = models.DecimalField(null=True, blank=False, default=0, max_digits=10, decimal_places=1)
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'User Credit Balance'
        verbose_name_plural = 'User Credit Balances'

@receiver(post_save, sender=SmsangoSBulkCredit)
def notifiy_admin(sender, **kwargs):
    from coreconfig.models import DashboardConfig
    try:
        smscredit_user = kwargs["instance"]
        send_mail(
            'A user\'s wallet has been Updated',
            '{}\'s Wallet Balance just changed to {}'.format(smscredit_user.user.username, smscredit_user.smscredit),
            settings.THEME_CONTACT_EMAIL,
            [DashboardConfig.objects.all()[0].email, ],
            fail_silently=False,
        )
        print("email sent")
    except:
        pass

class APIUrl(models.Model):
    api_name = models.CharField(null = True, blank = True, max_length=10, default='Default')
    apurl = models.TextField(null=True, blank=True)
    apurl_data = models.JSONField(default=dict, help_text='{"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "to":"[TO]", "sender":"[SENDER]", "message":"[MESSAGE]"}, "headers":{"authorization":"Bearer API_KEY"}}')    
    apiamtpersms = models.DecimalField(null=True, blank=False, default=2, max_digits=10, decimal_places=1)
    api_response = models.CharField(null = True, blank = True, max_length=20, default="")
    is_active = models.BooleanField()
    send_one_by_one = models.BooleanField(default=False, help_text=mark_safe("<strong style='color:red;'>if API can accept unlimited request per seconds check to True else False</strong>")) 

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'SMS API'
        verbose_name_plural = 'SMS APIs'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    location = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(default='', blank=True, null=True)
    phone = models.CharField(max_length=15, default='', blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    refferal = models.CharField(max_length=30, blank=True, null=True)
    session_key = models.CharField(max_length=200, blank=True, null=True)
    
    transaction_pin = models.CharField(max_length=10, blank=True, null=True)
    kyc_verification = models.BooleanField(default=False, help_text="this is for bvn")
    kyc_verification_nin = models.BooleanField(default=False)
    nin_kyc = models.CharField(max_length=200, blank=True, null=True)
    bvn_kyc = models.CharField(max_length=200, blank=True, null=True)
    verification_response = models.TextField(null=True, blank=True, help_text="this is for bvn")
    verification_response_nin = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username
    @property
    def is_staff(self):
    	return self.is_admin
    def has_perm(self, perm, obj=None):
    	return self.is_admin
    def has_module_perms(self, app_label):
    	return self.is_admin


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()
        smsangosbulkcredit = SmsangoSBulkCredit(user=kwargs.get('instance'))
        smsangosbulkcredit.save()
        pricepersmstopurchase = PricingPerSMSPerUserToPurchase(user=kwargs.get('instance'))
        pricepersmstopurchase.save()
        bonusaccount = BonusAccount(user=kwargs.get('instance'))
        bonusaccount.save()
        if DashboardConfig.objects.all().exists():
            if DashboardConfig.objects.all()[0].allow_payment_for_apikey is False:
                token, created = Token.objects.get_or_create(user=user)


