from django.contrib import admin

# Register your models here.
from .models import *


class BonusesPercentageAdmin(admin.ModelAdmin):
    list_display = ('bonus_name', 'is_active', 'purchase_airtime_bonus', 'purchase_data_bonus', 'purchase_electricity_bonus', 'referral_bonus')
    list_filter = ('bonus_name','is_active')
    search_fields = ('bonus_name',)
    ordering = ('-is_active',)

    def save_model(self, request, obj, form, change):
        try:
            if len(BonusesPercentage.objects.all()) == 0:
                pass
            else:
                for i in BonusesPercentage.objects.all():
                    if obj is not i:
                        print(i)
                        disableOtherApis = BonusesPercentage.objects.get(id=i.id)
                        disableOtherApis.is_active = False
                        disableOtherApis.save()
        except Exception as e:
            pass
        super().save_model(request,obj, form, change)

admin.site.register(BonusesPercentage, BonusesPercentageAdmin)