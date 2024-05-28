from django.db import models

# Create your models here.

class SmtpEmailSettings(models.Model):
  smtp_email_host = models.CharField(max_length=500, default='smtp.example.com')
  smtp_email_host_user = models.CharField(max_length=500, default='apikey')
  smtp_email_host_sender_address = models.CharField(max_length=500, default='example@example.com')
  smtp_email_host_password = models.CharField(max_length=500, default='password')
  smtp_email_host_port = models.IntegerField(default='587')
  smtp_use_tls = models.BooleanField(default=False)
  smtp_use_ssl = models.BooleanField(default=False)
  smtp_timeout = models.IntegerField(default=10)
  is_active = models.BooleanField(default=False)

  def __str__(self):
    return 'Email configuration'
  
  class Meta:
    verbose_name = 'Email Configuration'
    verbose_name_plural = 'Email Configurations'


class SentEmails(models.Model):
  email_subject = models.CharField(max_length=500)
  email_content = models.TextField(max_length=10000, blank=True, null=True)
  recipient = models.TextField(max_length=10000, blank=True, null=True)
  status = models.CharField(max_length=50, default="Sent", blank=True, null=True)
  date_created = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.email_subject + '/' + str(self.date_created)