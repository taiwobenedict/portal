from django.contrib import admin
from cryptocurrency.models import *

class CryptoCurrenciesAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'amount', 'trans_id','status', 'date')
    list_filter = ('date',)
    search_fields = ('user','trans_id',)
    ordering = ('-date',)


admin.site.register(CryptoCurrencies, CryptoCurrenciesAdmin)
admin.site.register(CryptoCurrencyAPI)
