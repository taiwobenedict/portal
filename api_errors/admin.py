from django.contrib import admin
from api_errors.models import ErrorResponses

class ErrorResponsesAdmin(admin.ModelAdmin):
  list_display = ('name_of_api', 'error_name', 'error_code', 'error_description')
  list_filter = ('name_of_api', 'error_name',)
  search_fields = ('name_of_api', 'error_name',)
  ordering = ('-name_of_api',)
  list_editable = ('error_name', 'error_code', 'error_description')

admin.site.register(ErrorResponses, ErrorResponsesAdmin)
