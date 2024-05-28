from user_transactions.models import AllUserTransactionsLogs
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
# Create your models here.

class SmileTransactions(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smile_user')
  amount = models.FloatField()
  api_code = models.CharField(max_length=500, default='', blank=True, null=True)
  numberRecharged= models.CharField(max_length=500, default='', blank=True, null=True)
  smileType = models.CharField(max_length=500, default='', blank=True, null=True)
  resp = models.TextField(default='', blank=True, null=True)
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  status = models.CharField(max_length=100, default='', blank=True, null=True)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'Smile Transaction'
    verbose_name_plural = 'Smile Transactions'

@receiver(post_save, sender=SmileTransactions)
def smile_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = "Smile",
        trans_id = obj.trans_id,
        status = obj.status,
        amount = obj.amount,
        log = f"Smile Purchase: {obj.user.username} attempted to purchase Smile on ({obj.numberRecharged}) at {obj.date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )


class SpectranetTransactions(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spectranet_user')
  amount = models.FloatField()
  api_code = models.CharField(max_length=500, default='', blank=True, null=True)
  numberRecharged= models.CharField(max_length=500, default='', blank=True, null=True)
  resp = models.TextField(default='', blank=True, null=True)
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  status = models.CharField(max_length=100, default='', blank=True, null=True)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'Spectranet Transaction'
    verbose_name_plural = 'Spectranet Transactions'

@receiver(post_save, sender=SpectranetTransactions)
def spectranet_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = "Spectranet",
        trans_id = obj.trans_id,
        status = obj.status,
        amount = obj.amount,
        log = f"Spectranet Purchase: {obj.user.username} attempted to purchase Spectranet on ({obj.numberRecharged}) at {obj.date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )



class IntAirtimeTransactions(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='int_airtime_user')
  amount = models.FloatField()
  api_code = models.CharField(max_length=500, default='', blank=True, null=True)
  numberRecharged= models.CharField(max_length=500, default='', blank=True, null=True)
  network_recharged = models.CharField(max_length=500, default='', blank=True, null=True)
  country = models.CharField(max_length=500, default='', blank=True, null=True)
  resp = models.TextField(default='', blank=True, null=True)
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  status = models.CharField(max_length=100, default='', blank=True, null=True)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'International Airtime Transaction'
    verbose_name_plural = 'International Airtime Transactions'

@receiver(post_save, sender=IntAirtimeTransactions)
def intl_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.network_recharged,
        trans_id = obj.trans_id,
        status = obj.status,
        amount = obj.amount,
        log = f"{obj.user.username} attempted to purchase {obj.network_recharged} ({obj.country}) at {obj.date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )



class SmilesApis(models.Model):
  """Model definition for SMILE."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://apiname.online/api/smile')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  check_api_url = models.TextField(max_length=1000, default='https://apiname.online/api/smile')
  check_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  smile_code_json = models.TextField(max_length=5000, default='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]', help_text='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]')
  res_params = models.TextField(max_length=3000, default='', help_text='The responses from api to display to the users e.g ["code", "pin", "serialNumber"] as seen on the API response')
  success_code = models.CharField(max_length=500, default='success response')
  success_check_code = models.CharField(max_length=500, default='success response')
  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  WAEC API."""
    verbose_name = 'SMILE API'
    verbose_name_plural = 'SMILE APIs'

class SpectranetApis(models.Model):
  """Model definition for Spectranet Apis."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://apiname.online/api/spectranet')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this =>{"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  spectranet_code_json = models.TextField(max_length=5000, default='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]', help_text='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]')
  res_params = models.TextField(max_length=3000, default='', help_text='The responses from api to display to the users e.g ["code", "pin", "serialNumber"] as seen on the API response')
  success_code = models.CharField(max_length=500, default='success response')
  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  SPECTRANET API."""
    verbose_name = 'SPECTRANET API'
    verbose_name_plural = 'SPECTRANET APIs'


class MtnSMEApi(models.Model):
  """Model definition for MtnSME Apis."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_api_url = models.TextField(max_length=1000, default='https://apiname.online/api/mtnSME')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  mtn_sme_code_json = models.TextField(max_length=5000, default='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]', help_text='["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]')
  success_code = models.CharField(max_length=500, default='success response')
  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  NECO API."""
    verbose_name = 'MTN SME API'
    verbose_name_plural = 'MTN SME APIs'

class IntAirtimeApi(models.Model):
  """Model definition for SMILE."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://apiname.online/api/smile')
  api_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  check_api_url = models.TextField(max_length=1000, default='https://apiname.online/api/smile')
  check_url_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[APIKEY]", "userid":"[USER_ID]", "typeno":"[SERVICE_CODE]", "typename":"[SERVICE_NAME]", "amount":"[AMOUNT]", "txref":"[TRANSACTION_ID]"}, "headers":{"AUTHORIZATION":"API_KEY OR SOMETHING"}}')
  res_params = models.TextField(max_length=3000, default='', help_text='The responses from api to display to the users e.g ["code", "pin", "serialNumber"] as seen on the API response')
  commission = models.IntegerField(default=0)
  success_code = models.CharField(max_length=500, default='success response')
  success_check_code = models.CharField(max_length=500, default='success response')
  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  WAEC API."""
    verbose_name = 'International Airtime API'
    verbose_name_plural = 'International Airtime APIs'