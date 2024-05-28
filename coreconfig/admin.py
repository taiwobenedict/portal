from django.contrib import admin

# Register your models here.
from .models import DashboardConfig, DisplayOfApps

class DashboardConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class DisplayOfAppsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
    
admin.site.register(DashboardConfig, DashboardConfigAdmin)
admin.site.register(DisplayOfApps, DisplayOfAppsAdmin)
