from django.contrib import admin

from voucher.models import GeneratedVoucher, UsedVouchers

class GeneratedVoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'voucher_amount', 'date', 'status')
    list_filter = ('date', 'status',)
    search_fields = ('voucher','status',)
    ordering = ('-date',)

class UsedVouchersAdmin(admin.ModelAdmin):
    list_display = ('user', 'voucher', 'status', 'date')
    list_filter = ('date', 'status',)
    search_fields = ('user', 'voucher','status',)
    ordering = ('-date',)

admin.site.register(GeneratedVoucher, GeneratedVoucherAdmin)
admin.site.register(UsedVouchers, UsedVouchersAdmin)