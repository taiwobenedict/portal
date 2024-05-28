from django.contrib import admin

from rechargeapp.models import CableRecharegAPI,DataNetworks,RechargeAirtimeAPI,AirtimeTopup,CableRecharge,DataPlansPrices,BonusAccount,MtnDataShare,RefBonusAccount

class MtnDataShareDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordernumber', 'data_amount', 'old_balance', 'new_balance', 'data_network', 'data_number', 'dataSize', 'batchno', 'status', 'purchased_date')
    list_filter = ('purchased_date',)
    search_fields = ('user__username','user__email','ordernumber',)
    ordering = ('-purchased_date',)

class AirtimeTopupDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordernumber', 'recharge_amount', 'old_balance', 'new_balance', 'recharge_network', 'recharge_number','status', 'purchased_date')
    list_filter = ('purchased_date',)
    search_fields = ('user__username','user__email','ordernumber',)
    ordering = ('-purchased_date',)

class RechargeAirtimeAPIAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'api_url', 'identifier', 'is_active', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name','success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True

class DataNetworksAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'is_active', 'identifier', 'api_url', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name','success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True

class CableRecharegAPIAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'is_active', 'api_url', 'identifier', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name','success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True

class CableRecharegesAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordernumber', 'sub_amount', 'billtype', 'smart_no','status', 'old_balance', 'new_balance', 'purchased_date')
    list_filter = ('purchased_date',)
    search_fields = ('user__username','user__email','ordernumber',)
    ordering = ('-purchased_date',)

admin.site.register(CableRecharegAPI, CableRecharegAPIAdmin)

admin.site.register(DataNetworks, DataNetworksAdmin)
admin.site.register(RechargeAirtimeAPI, RechargeAirtimeAPIAdmin)
# admin.site.register(AirtimeTopup, AirtimeTopupDetailsAdmin)
# admin.site.register(CableRecharge, CableRecharegesAdmin)
# admin.site.register(DataPlansPrices)
# admin.site.register(MtnDataShare, MtnDataShareDetailsAdmin)
admin.site.register(BonusAccount)
admin.site.register(RefBonusAccount)