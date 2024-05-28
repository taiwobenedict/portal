from django.contrib import admin
from education.models import *
# Register your models here.

class ResultCheckersAdmin(admin.ModelAdmin):
  list_display = ('user', 'pin_type', 'identifier', 'trans_id', 'old_balance', 'new_balance')
  list_filter = ('user',)
  search_fields = ('user__username','user__email',)
  ordering = ('-date',)

class ResultCheckerAPIsAdmin(admin.ModelAdmin):
  list_display = ('api_name', 'api_url', 'identifier', 'is_active', 'success_code')
  list_filter = ('api_name',)
  search_fields = ('api_name','success_code',)
  ordering = ('-api_name',)
  list_editable = ('is_active',)
  save_as = True


admin.site.register(ResultCheckers, ResultCheckersAdmin)
admin.site.register(ResultCheckerAPIs, ResultCheckerAPIsAdmin)