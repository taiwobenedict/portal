from django.contrib import admin
from mail.models import SmtpEmailSettings, SentEmails

admin.site.register(SmtpEmailSettings)
admin.site.register(SentEmails)