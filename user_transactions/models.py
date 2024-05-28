from django.db import models
from django.contrib.auth.models import User

class AllUserTransactionsLogs(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_transaction_log")
  service = models.CharField(default='', max_length=200, blank=True, null=True)
  trans_id = models.CharField(default='', max_length=200, blank=True, null=True)
  status = models.CharField(default='', max_length=200, blank=True, null=True)
  amount = models.CharField(default="", max_length=200, blank=True, null=True)
  log = models.TextField(default="", blank=True, null=True)
  old_balance = models.TextField(default="", blank=True, null=True)
  new_balance = models.TextField(default="", blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.service
  