from django.contrib import admin
from whatsapp_api.models import WhatsAppPurchaseAccess, WhatsAppSettings


class WhatsAppPurchaseAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    list_filter = ('user',)
    search_fields = ('user','is_active',)

admin.site.register(WhatsAppPurchaseAccess, WhatsAppPurchaseAccessAdmin)
admin.site.register(WhatsAppSettings)
