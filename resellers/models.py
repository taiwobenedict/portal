from user_transactions.models import AllUserTransactionsLogs
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

class ResellerStatus(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_reseller_status")
  is_reseller = models.BooleanField(default=False)
  reseller_level = models.CharField(max_length=100, default='Not a Reseller')
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  def __unicode__(self):
    return self.user.username

class ResellerLevelsAndPercentage(models.Model):
  name = models.CharField(max_length=100, default="Lever One Reseller")
  is_active = models.BooleanField(default=False)
  cost_of_activation = models.FloatField(default=0.0, help_text="amount to be paid by the user to join this level of reseller")
  fund_to_wallet = models.FloatField(default=1000.0, help_text="Minimum amount to fund into wallet")
  airtime = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  data = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  education = models.TextField(default='{"education1": 0.01, "education2":0.02}', help_text='this should be in json format e.g {"education1": 0.01, "education2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  electricity = models.TextField(default='{"electicity1": 0.01, "electicity2":0.02}', help_text='this should be in json format e.g {"electicity1": 0.01, "electicity2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  cable_tv = models.TextField(default='{"cable1": 0.01, "cable2":0.02}', help_text='this should be in json format e.g {"cable1": 0.01, "cable2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  insurance = models.TextField(default='{"Private": 0.01}', help_text='this should be in json format e.g {"Private": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  health_insurance = models.TextField(default='{"individual-monthly": 0.01}', help_text='this should be in json format e.g {"individual-monthly": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  home_cover = models.TextField(default='{"individual-monthly": 0.01}', help_text='this should be in json format e.g {"individual-monthly": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  personal_insurance = models.TextField(default='{"individual-monthly": 0.01}', help_text='this should be in json format e.g {"individual-monthly": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  decoded_card_printing = models.TextField(default='{"network1": 0.01, "network2":0.02}', help_text='this should be in json format e.g {"network1": 0.01, "network2":0.02} where 0.01 means 1%, network1 is the network code as in your API')
  smile = models.TextField(default='{"sms": 0.01}', help_text='this should be in json format e.g {"sms": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  mtn_sme = models.TextField(default='{"sms": 0.01}', help_text='this should be in json format e.g {"sms": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  spectranet = models.TextField(default='{"sms": 0.01}', help_text='this should be in json format e.g {"sms": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')
  sms = models.TextField(default='{"sms": 0.01}', help_text='this should be in json format e.g {"sms": 0.01} where 0.01 means 1%, her only the percentage amount should be affected leave "sms" as is on change the 0.01 to your preferred percentage')

  def __str__(self):
    return self.name

  def __unicode__(self):
    return self.name

class ResellerHistory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reseller_history")
  amount = models.FloatField(default=0.0)
  old_balance = models.FloatField(default=0.0)
  new_balance = models.FloatField(default=0.0)
  reseller_level = models.CharField(max_length=100, default="")
  previous_reseller_level = models.CharField(max_length=100, default="")
  action = models.CharField(max_length=100, default="")
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  def __unicode__(self):
    return self.user.username

@receiver(post_save, sender=ResellerHistory)
def cardp_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = "reseller",
        trans_id = "",
        status = obj.action,
        amount = obj.amount,
        log = f"ResellerHistory: {obj.user.username} attempted to {obj.action} to {obj.reseller_level} reseller on {obj.date}",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )
