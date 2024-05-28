from django.contrib import admin

# Register your models here.
from monnify_app.models import *

class MonnifyKeysAdmin(admin.ModelAdmin):
    list_display = ('apiKey', 'clientSecret', 'currencyCode', 'contractCode')

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

class MonnifyAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'accountReference', 'accountNumber', 'accountName','bankName', 'bankCode', 'customerEmail')

admin.site.register(MonnifyKeys, MonnifyKeysAdmin)
admin.site.register(MonnifyAccount, MonnifyAccountAdmin)
