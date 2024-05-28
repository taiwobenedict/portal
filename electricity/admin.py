from django.contrib import admin
from electricity.models import *
# Register your models here.


class ElectricityAdmin(admin.ModelAdmin):
  list_display = ('user', 'identifier', 'meter_no', 'trans_id', 'old_balance', 'new_balance')
  list_filter = ('user',)
  search_fields = ('user__username','user__email',)
  ordering = ('-date',)

class ElectricityApisAdmin(admin.ModelAdmin):
  list_display = ('api_name', 'api_url', 'identifier', 'is_active', 'success_code')
  list_filter = ('api_name',)
  search_fields = ('api_name','success_code',)
  ordering = ('-api_name',)
  list_editable = ('is_active',)
  save_as = True

admin.site.register(Electricity, ElectricityAdmin)
admin.site.register(ElectricityApis, ElectricityApisAdmin)