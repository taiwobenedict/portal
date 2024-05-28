from django.contrib import admin

# Register your models here.
from .models import *

class PayStackPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_id', 'amount','old_balance', 'new_balance', 'smsangosbulkcredit', 'reference', 'amtcredited', 'dated')
    search_fields = ('user__username', 'user__email','dated','order_id',)
    ordering = ('-dated',)

admin.site.register(PayStackPayment, PayStackPaymentAdmin)
