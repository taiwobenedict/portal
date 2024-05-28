from user_transactions.models import AllUserTransactionsLogs
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
# Create your models here.

class CryptoCurrencies(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_buyer')
  currency = models.CharField(max_length=100, default='')
  amount = models.FloatField()
  trans_id = models.CharField(max_length=100, default='', blank=True, null=True)
  status = models.CharField(max_length=100, choices=(('DONE','DONE'), ('NOT DONE','NOT DONE')))
  date = models.DateField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  class Meta:
    db_table = ''
    managed = True
    verbose_name = 'Crypto Currency'
    verbose_name_plural = 'Crypto Currencies'

@receiver(post_save, sender=CryptoCurrencies)
def crypto_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = obj.currency,
        trans_id = obj.trans_id,
        status = obj.status,
        amount = obj.amount,
        log = f"Crypto Currencies: {obj.user.username} attempted to purchase Crypto Currencies on {obj.date} ({obj.status})",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )


class CryptoCurrencyAPI(models.Model):
  """Model definition for Crypto Currency API."""
  api_name = models.CharField(max_length=30, default='app name')
  is_active = models.BooleanField(default=False)
  api_url = models.TextField(max_length=1000, default='https://api.whatsapp.com/send?phone=[ENTER_NUMBER]&text=I am interested in buying/selling [CRYPTO_CURRENCY] TRANSACTION ID is [TRANSACTION_ID]', help_text="WhatsApp Link with number")
  currencies_trading = models.TextField(max_length=5000, default='["Bitcoin","Etherium"]')
  def __str__(self):
      return self.api_name

  class Meta:
    """Meta definition for  WAEC API."""
    verbose_name = 'Crypto Currency API'
    verbose_name_plural = 'Crypto Currency APIs'
