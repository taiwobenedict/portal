from django.contrib import admin
from user_transactions.models import AllUserTransactionsLogs

class AllUserTransactionsLogsAdmin(admin.ModelAdmin):
  list_display = ('user', 'service', 'status', 'trans_id', 'amount', 'old_balance', 'new_balance', 'log', 'created_at')
  list_filter = ('service',)
  search_fields = ('service', 'user__username',)
  ordering = ('-created_at',)

admin.site.register(AllUserTransactionsLogs, AllUserTransactionsLogsAdmin)
