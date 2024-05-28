from django.contrib import admin

# Register your models here.
from notificationapp.models import *

admin.site.register(Notification)
admin.site.register(ReadNotification)
