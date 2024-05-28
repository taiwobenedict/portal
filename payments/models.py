from django.db import models
from smsangosend.models import *


class PayStackPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_purchase")
    smsangosbulkcredit = models.ForeignKey(SmsangoSBulkCredit, on_delete=models.CASCADE, related_name="paystack_purchase")
    order_id = models.CharField(max_length=100,blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    amtcredited = models.FloatField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    dated = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.order_id)+ '-' +str(self.user.username)

    class Meta:
      managed = True
      verbose_name = 'Payment History'
      verbose_name_plural = 'Payments & Voucher Histories'

@receiver(post_save, sender=PayStackPayment)
def payment_post_save_receiver(sender, **kwargs):
    obj = kwargs["instance"]
    AllUserTransactionsLogs.objects.create(
        user = obj.user,
        service = "funding account",
        trans_id = obj.reference,
        status = "",
        amount = obj.amount,
        log = f"Funding Wallet: {obj.user.username} attempted to fund wallet with {obj.amount} on {obj.dated}",
        old_balance = obj.old_balance,
        new_balance = obj.new_balance
    )

class SMSVolumePlan(models.Model):
    plan_name = models.CharField(max_length=30, null=True, blank=True)
    volume = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.plan_name
