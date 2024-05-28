from django.contrib import admin
from django.contrib import messages
from alert_system.models import *

class AlertAdminSystem(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_times','created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
      try:
        if len(AlertSystem.objects.all()) == 0:
          pass
        else:
          for i in AlertSystem.objects.all():
            if obj is not i:
              disableOtherApis = AlertSystem.objects.get(id=i.id)
              disableOtherApis.is_active = False
              disableOtherApis.save()
        super().save_model(request,obj, form, change)
      except Exception as e:
        pass


class TutorialNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pin_to_top', 'url','created_at')
    list_filter = ('created_at', 'pin_to_top',)
    search_fields = ('title',)
    ordering = ('-created_at',)


admin.site.register(AlertSystem, AlertAdminSystem)
admin.site.register(UserReadAlert)
admin.site.register(TutorialNews, TutorialNewsAdmin)