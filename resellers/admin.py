from django.contrib import admin

from resellers.models import ResellerLevelsAndPercentage, ResellerStatus, ResellerHistory

class ResellerLevelsAndPercentageAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost_of_activation', 'fund_to_wallet', 'airtime', 'data', 'electricity', 'education', 'cable_tv')
    search_fields = ('name',)

class ResellerStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_reseller', 'reseller_level', 'date')
    search_fields = ('user__username','reseller_level',)
    ordering = ('-date',)

class ResellerHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount','old_balance', 'new_balance',  'previous_reseller_level', 'reseller_level', 'date')
    search_fields = ('user__username','reseller_level',)
    ordering = ('-date',)

admin.site.register(ResellerLevelsAndPercentage, ResellerLevelsAndPercentageAdmin)
admin.site.register(ResellerStatus, ResellerStatusAdmin)
admin.site.register(ResellerHistory, ResellerHistoryAdmin)
