import json
from user_transactions.models import AllUserTransactionsLogs
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

# Create your models here.

class ResultCheckers(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='result_check_buyer')
  amount = models.FloatField()
  pin = models.CharField(max_length=1000, default='', blank=True, null=True)
  identifier = models.CharField(max_length=50, default='waec_airtime', help_text='this should be a unique identifier')
  serial_number = models.CharField(max_length=1000, default='', blank=True, null=True)
  pin_type = models.CharField(max_length=500, default='', blank=True, null=True)
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  api_response = models.TextField(max_length=13000, default='', blank=True, null=True)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  status = models.CharField(max_length=100, default='', blank=True, null=True)
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    db_table = ''
    managed = True
    verbose_name = 'ResultCheckers Transaction'
    verbose_name_plural = 'ResultCheckers Transactions'

@receiver(post_save, sender=ResultCheckers)
def result_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.identifier,
        trans_id = obj.trans_id,
        status = obj.status,
        amount = obj.amount,
        log = f"{obj.user.username} attempted to purchase {obj.identifier} at {obj.date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )

def jsonfield_default_value():  # This is a callable
    return json.dumps({"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}})

class ResultCheckerAPIs(models.Model):
  """Model definition for Registration Card API."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://apiname.online/api/waec')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}, then edit suit you')
  identifier = models.CharField(max_length=50, default='waec_airtime', help_text='this should be a unique identifier')
  result_checker_image = models.ImageField(default="", help_text="the best image needed here is a square image recommended is 500 x 500")
  pin_code_json = models.TextField(max_length=1000, default='[api_price|site_price|what_the_user_see]')
  res_params = models.TextField(max_length=3000, default='', help_text='The responses from api to display to the users e.g ["code", "pin", "serialNumber"] as seen on the API response')
  success_code = models.CharField(max_length=500, default='success')
  description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  WAEC API."""
    verbose_name = 'ResultChecker API'
    verbose_name_plural = 'ResultChecker APIs'
