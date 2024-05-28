from django.contrib import admin

# Register your models here.
from rave_payment.models import *

class RavePayKeysAdmin(admin.ModelAdmin):
    list_display = ('public_key', 'secret_key', 'encryption_key', 'rave_fee', 'funding_limit')

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

admin.site.register(RaveConfiguration, RavePayKeysAdmin)
