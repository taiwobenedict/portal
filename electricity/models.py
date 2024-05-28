from user_transactions.models import AllUserTransactionsLogs
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
# Create your models here.

class Electricity(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elctricity_user')
  identifier = models.CharField(max_length=50, default='electricity_code', help_text='this should be a unique identifier')
  email = models.EmailField(max_length=254, blank=True, null=True)
  phone = models.CharField(max_length=100, blank=True, null=True)
  amount = models.FloatField()
  service = models.CharField(max_length=100, default='', blank=True, null=True)
  meter_no = models.CharField(max_length=100, default='', blank=True, null=True)
  customer_name = models.CharField(max_length=500, default='', blank=True, null=True)
  customer_address = models.CharField(max_length=500, default='', blank=True, null=True)
  customer_account_type = models.CharField(max_length=300, default='', blank=True, null=True)
  customer_dt_number = models.CharField(max_length=100, default='', blank=True, null=True)
  api_response = models.TextField(default='', blank=True, null=True)
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  status = models.CharField(max_length=100, default='', blank=True, null=True)
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    db_table = ''
    managed = True
    verbose_name = 'Electricity Transaction'
    verbose_name_plural = 'Electricity Transactions'

@receiver(post_save, sender=Electricity)
def electricity_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.identifier,
        trans_id = obj.trans_id,
        status = "",
        amount = obj.amount,
        log = f"{obj.user.username} attempted to purchase {obj.identifier} at {obj.date}",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )


class ElectricityApis(models.Model):
  """Model definition for ElectricityApis."""
  api_name = models.CharField(max_length=30, default='1app')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://apiname.online/api/elect')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "account":"[METER_NO]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]", "custnam":"[CUSTOMER_NAME]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}, then edit suit you')
  identifier = models.CharField(max_length=50, default='airtime', help_text='this should be a unique identifier')
  electricity_image = models.ImageField(default="", help_text="the best image needed here is a square image recommended is 500 x 500")
  api_url_check = models.TextField(max_length=1000, default='https://{{request.get_host}}/app/api/v1/check_electricity?meterNo=[METER_NO]&service=[SERVICE]')
  api_url_balance = models.TextField(max_length=1000, default='None')
  electricity_code_json = models.TextField(max_length=5000, default="EKO_POSTPAID|Eko Electricity Distribution Postpaid|13|Eko Postpaid")
  metertype_code_json = models.TextField(max_length=500, default='["01|Prepaid","02|Postpaid"]')
  check_success_code = models.CharField(max_length=500, default='customerName')
  res_params = models.TextField(default='', help_text='The responses from api to display to the users e.g ["code", "pin", "serialNumber"] as seen on the API response')
  commission = models.FloatField(default=0.0)
  success_code = models.CharField(max_length=500, default='success')
  description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

  def __str__(self):
      return self.api_name
  # TODO: Define fields here

  class Meta:
    """Meta definition for ElectricityApis."""
    verbose_name = 'ElectricityApi'
    verbose_name_plural = 'ElectricityApis'
