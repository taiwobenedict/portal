from django.contrib import admin

# Register your models here.

from api.models import ApiKeyActivation, KycApi


class ApiKeyActivationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_paid')
    list_filter = ('user',)
    search_fields = ('user','is_paid',)

class KycApiAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name','is_active',)

admin.site.register(ApiKeyActivation, ApiKeyActivationAdmin)
admin.site.register(KycApi, KycApiAdmin)
