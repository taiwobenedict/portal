from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class GeneratedVoucher(models.Model):
  voucher = models.CharField(max_length=30, default='', blank=True, null=True)
  voucher_amount = models.IntegerField()
  status = models.CharField(max_length=7, default='UN-USED')
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.voucher

  def __unicode__(self):
    return self.voucher

class UsedVouchers(models.Model):
  voucher = models.ForeignKey(GeneratedVoucher, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_used_voucher")
  status = models.CharField(max_length=7, default='')
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.username

  def __unicode__(self):
    return self.user.username