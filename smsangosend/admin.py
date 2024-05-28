from django.contrib import admin

# Register your models here.
from .models import *
# from smsangonumcredit.models import NumberCredits
class SmsangoSBulkCreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'smscredit')
    search_fields = ['user__username']
    list_editable = ('smscredit',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'phone']

    def user_email(self, obj):
    	return obj.user.email
    user_email.admin_order_field = 'email'

class APIUrlAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'apurl', 'apiamtpersms', 'api_response', 'is_active')


admin.site.register(SmsangoSendSMS)
# admin.site.register(LogEntry)
admin.site.register(SmsangoSBulkCredit, SmsangoSBulkCreditAdmin)
admin.site.register(UserProfile)
admin.site.register(APIUrl, APIUrlAdmin)
admin.site.register(PhoneBookContacts)
admin.site.register(SavedScheduledSMS)
