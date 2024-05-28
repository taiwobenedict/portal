# howdy/urls.py
from django.conf.urls import url
from django.urls import path
from transactions.views import *

app_name='transactions'
urlpatterns = [
    path('transactions/', transactions, name='list_tranasactions'),
    path('transactions/<int:pk>/', singleOrderApiresponse, name='transaction_detail'),
    # path('all_transactions/', all_transactions, name='all_transactions'),
    # path('refund_transaction/', refund_transaction, name='refund_transaction'),
]
