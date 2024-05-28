# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from cryptocurrency.views import *

app_name='cryptocurrency'
urlpatterns = [
    #cryptocurrency API
    path('cryptoTransactions', cryptoTransactions, name='cryptoTransactions'),
    path('cryptoTemplate', cryptoCurrencyTemplate, name='cryptoTemplate'),
    path('cryptocurrencyPurchase', cryptoPurchase, name='cryptoPurchase'),
]