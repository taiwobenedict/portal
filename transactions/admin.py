from django.contrib import admin
from .models import Transactions


class TransactionTopupDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'reference', 'bill_type', 'actual_amount', 'paid_amount', 'old_balance', 'new_balance', 'status', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username','user__email','bill_type', 'reference',)
    ordering = ('-created_at',)

admin.site.register(Transactions, TransactionTopupDetailsAdmin)