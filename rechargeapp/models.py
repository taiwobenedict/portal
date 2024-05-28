import pytz
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, post_migrate
from django.dispatch import receiver

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from user_transactions.models import AllUserTransactionsLogs
from django.utils import timezone
import random, time
from django.core.exceptions import ValidationError

# Create your models here.
User = settings.AUTH_USER_MODEL

class AirtimeTopup(models.Model):
    user = models.ForeignKey(User, related_name='user_airtime', on_delete=models.CASCADE)
    identifier = models.CharField(default="", max_length=50)
    ordernumber = models.CharField(default='', max_length=20, blank=True, null=True)
    recharge_amount = models.FloatField(default=0, blank=True, null=True)
    recharge_network = models.CharField(default='', max_length=20, blank=True, null=True)
    recharge_number = models.CharField(default='', max_length=20, blank=True, null=True)
    api_response = models.TextField(default='', blank=True, null=True)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    status = models.TextField(default='',max_length=20, blank=True, null=True)
    purchased_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        time.sleep(random.randint(2, 5))
        getLastOne = AirtimeTopup.objects.all().last()

        if (int(timezone.now().timestamp()) - int(getLastOne.purchased_date.timestamp()) <= 30) and (getLastOne.user == self.user) and (self.recharge_number == getLastOne.recharge_number):
            raise ValidationError("Denied by fraud detection")
        else:
            super(AirtimeTopup, self).save(*args, **kwargs)

@receiver(post_save, sender=AirtimeTopup)
def airtime_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.identifier,
        trans_id = obj.ordernumber,
        status = obj.status,
        amount = obj.recharge_amount,
        log = f"{obj.user.username} attempted to purchase {obj.identifier} at {obj.purchased_date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )

class CableRecharge(models.Model):
    user = models.ForeignKey(User, related_name='user_cablerecharge', on_delete=models.CASCADE)
    identifier = models.CharField(default="", max_length=50)
    ordernumber = models.CharField(default='', max_length=50, blank=True, null=True)
    invoice = models.CharField(default='', max_length=30, blank=True, null=True)
    sub_amount = models.FloatField(default=0, blank=True, null=True)
    smart_no = models.CharField(default='', max_length=30, blank=True, null=True)
    billtype = models.CharField(default='', max_length=10, blank=True, null=True)
    customernumber = models.CharField(default='', max_length=30, blank=True, null=True)
    customername = models.CharField(default='', max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    exchange_reference = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(default='',max_length=100, blank=True, null=True)
    messageresp = models.TextField(default='', blank=True, null=True)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    purchased_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username


@receiver(post_save, sender=CableRecharge)
def cable_post_save_receiver(sender, **kwargs):
    cable = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = cable.user,
        service = cable.identifier,
        trans_id = cable.ordernumber,
        status = cable.status,
        amount = cable.sub_amount,
        log = f"{cable.user.username} attempted to purchase {cable.identifier} at {cable.purchased_date} ({cable.status})",
        old_balance = cable.old_balance,
        new_balance = cable.new_balance
    )
    



class DataPlansPrices(models.Model):
    mtn = models.TextField(default='', max_length='1000', blank=True, null=True)
    airtel = models.TextField(default='', max_length='1000', blank=True, null=True)
    glo = models.TextField(default='', max_length='1000', blank=True, null=True)
    nine_mobile = models.TextField(default='', max_length='1000', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    def __str__(self):
        return ("Data Prices")
    
class BonusAccount(models.Model):
    user = models.OneToOneField(User, related_name='user_bonus', on_delete=models.CASCADE)
    oldbonus = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, blank=True, null=True)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
 
class RefBonusAccount(models.Model):
    user = models.ForeignKey(User, related_name='refuser_bonus', on_delete=models.CASCADE)
    refbonus = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    refoldbonus = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    redeemed = models.CharField(default='', max_length=20, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class MtnDataShare(models.Model):
    user = models.ForeignKey(User, related_name='user_mtndatashare', on_delete=models.CASCADE)
    identifier = models.CharField(default="", max_length=50)
    ordernumber = models.CharField(default='', max_length=20, blank=True, null=True)
    data_amount = models.IntegerField(default=0, blank=True, null=True)
    data_network = models.CharField(default='MTN', max_length=20, blank=True, null=True)
    dataSize = models.CharField(default='', max_length=20, blank=True, null=True)
    data_number = models.CharField(default='', max_length=20, blank=True, null=True)
    batchno = models.CharField(default='', max_length=20, blank=True, null=True)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    api_response = models.TextField(default='', blank=True, null=True)
    status = models.TextField(default='',max_length=100, blank=True, null=True)
    purchased_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Data Top Up'
        verbose_name_plural = 'Data TopUps'

    def save(self, *args, **kwargs):
        time.sleep(random.randint(2, 5))
        getLastOne = MtnDataShare.objects.all().last()

        if (int(timezone.now().timestamp()) - int(getLastOne.purchased_date.timestamp()) <= settings.TIME_IN_SECONDS_INTERVAL_TO_PREVENT_DOUBLE_RECHARGE) and (getLastOne.user == self.user) and (self.data_number == getLastOne.data_number):
            raise ValidationError("Denied by fraud detection")
        else:
            super(MtnDataShare, self).save(*args, **kwargs)

@receiver(post_save, sender=MtnDataShare)
def data_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.identifier,
        trans_id = obj.ordernumber,
        status = obj.status,
        amount = obj.data_amount,
        log = f"{obj.user.username} attempted to purchase {obj.identifier} at {obj.purchased_date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )


class RechargeAirtimeAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    is_active = models.BooleanField(default=False)
    network_image = models.ImageField(default="", help_text="the best image needed here is a square image recommended is 500 x 500")
    identifier = models.CharField(max_length=50,   default='waec_airtime', help_text='this should be a unique identifier')
    api_url = models.TextField(max_length=1000, default='https://apiname.online/api/airtime')
    api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "network_id":"[network_code]", "amount":"[amt]", "phoneno":"[phone]"}, "headers":{"authorization": "Bearer (API_KEY)"}}, then edit suit you')
    api_url_balance = models.TextField(max_length=1000, default='https://apiname.online/api/balance?userid=[Enter_userid]&apikey=[Apikey]')
    user_discount = models.FloatField(default=0.0, help_text=mark_safe("<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    success_code = models.CharField(max_length=500, default='true')
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Airtime Recharge'
        verbose_name_plural = 'APIs For Airtime Recharge'

class DataNetworks(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    is_active = models.BooleanField(default=False)
    network_image = models.ImageField(default="", help_text="the best image needed here is a square image recommended is 500 x 500")
    identifier = models.CharField(max_length=50,  default='waec_airtime', help_text='this should be a unique identifier')
    api_url = models.TextField(max_length=1000, default='https://apiname.online/api/databundle')
    api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "network_id":"[urlvariable]", "amount":"[apiamount]", "datacode":"[dataplan]","phoneno":"[phone]"}, "headers":{"authorization":"Bearer API_KEY"}}, then edit suit you')
    api_url_balance = models.TextField(max_length=1000, default='https://apiname.online/api/balance?userid=[Enter_userid]&apikey=[Apikey]')
    success_code = models.CharField(max_length=500, default='true')
    network_data_amount_json = models.TextField(max_length=13000, default='220|500MB_(SME)|1|500MB (SME)@NGN220|extravariable,410|1GB_(SME)|1|1GB (SME)@NGN410|extravariable', help_text=mark_safe("<strong style='color:red;'>apiamount|data_amount|portal_api_code|what_user_sees|extravariable'</strong>"))
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Data Recharge'
        verbose_name_plural = 'APIs For Data Recharge'

class CableRecharegAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    is_active = models.BooleanField(default=False)
    api_url = models.TextField(max_length=1000, default='https://apiname.online/api/cable')
    api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "iuc":"[SMART_NO]", "type":"[SERVICE]","amount":"[PLAN_AMOUNT]", "custno":"[CUSTOMER_NUMBER]", "custname":"[CUSTOMER_NAME]", "txref":"[ORDER_NUMBER]"}, "headers":{"authorization":"Bearer API_KEY"}}, then edit suit you')
    api_url_balance = models.TextField(max_length=1000, default='https://apiname.online/api/balance?userid=[Enter_userid]&apikey=[Apikey]')
    identifier = models.CharField(max_length=50, default='waec_airtime', help_text='this should be a unique identifier')
    cable_image = models.ImageField(default="", help_text="the best image needed here is a square image recommended is 500 x 500")
    customerCheck = models.TextField(max_length=1000, default='https://{{request.get_host}}/app/customer/recharge/cable-check.aspx?smart_no=[SMART_NO]&service=[SERVICE]')
    cable_type_price = models.TextField(max_length=13000, default='["|select a DSTV package", "ACSSE36|DStv Access = N2000 + Convinience fee N50|2050|2050", "FTAE36|DStv FTA Plus = N1600 + Convinience fee N50|1650|1650", "COFAME36|DStv Family = N4000 + Convinience fee N50|4050|4050", "ASIAE36|DstvAsiaBouqet = N5400 + Convinience fee N50|5450|5450", "COMPE36|DStv Compact = N6800 + Convinience fee N50|6850|6850", "COMPLE36|DStv Plus = N10650 + Convinience fee N50|10700|10700", "PRWE36|Dstv Premium = N15800 + Convinience fee N50|15850|15850", "DPRHD|DStv Premium Asia Ex= N19900 + Convinience fee N50|19950|19950", "DPRHDP|Dstv Premium Extra = N18000 + Convinience fee N50|18050|18050"]', help_text=mark_safe('<span class="text-danger">["api_code|what_user_sees|api_price|site_price|site_service_code"]</span>'))
    success_code = models.CharField(max_length=500, default='true')
    successCheckCode = models.CharField(max_length=500, default='true')
    res_params = models.TextField(max_length=3000, default='', help_text='The responses from api to display to the users e.g ["code", "variabletwo"] as seen on the API response')
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Cable Recharge'
        verbose_name_plural = 'APIs For Cable Recharge'

