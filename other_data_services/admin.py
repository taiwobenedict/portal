from django.contrib import admin
from other_data_services.models import *
# Register your models here.

class SmileTransactionsAdmin(admin.ModelAdmin):
  list_display = ('user', 'amount', 'api_code', 'numberRecharged', 'trans_id', 'status', 'old_balance', 'new_balance')
  list_filter = ('user',)
  search_fields = ('user__username','user__email',)
  ordering = ('-date',)

class SpectranetTransactionsAdmin(admin.ModelAdmin):
  list_display = ('user', 'amount', 'api_code', 'numberRecharged', 'trans_id', 'status', 'old_balance', 'new_balance')
  list_filter = ('user',)
  search_fields = ('user__username','user__email',)
  ordering = ('-date',)

class SmilesApisAdmin(admin.ModelAdmin):
  list_display = ('api_name', 'api_url', 'api_url_data', 'is_active', 'success_code')
  list_filter = ('api_name',)
  search_fields = ('api_name','success_code',)
  ordering = ('-api_name',)
  list_editable = ('is_active',)

class SpectranetApisAdmin(admin.ModelAdmin):
  list_display = ('api_name', 'api_url', 'api_url_data', 'is_active', 'success_code')
  list_filter = ('api_name',)
  search_fields = ('api_name','success_code',)
  ordering = ('-api_name',)
  list_editable = ('is_active',)

admin.site.register(SmileTransactions, SmileTransactionsAdmin)
admin.site.register(SpectranetTransactions, SpectranetTransactionsAdmin)
admin.site.register(SmilesApis, SmilesApisAdmin)
admin.site.register(SpectranetApis, SpectranetApisAdmin)
admin.site.register(IntAirtimeApi)
admin.site.register(IntAirtimeTransactions)