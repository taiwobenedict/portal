# howdy/urls.py
from django.conf.urls import url
from django.urls import path
from user_transactions.views import *

app_name='user_transactions'
urlpatterns = [
    path('user_transactions/', listUserTranasactions, name='list_user_tranasactions'),
    path('transaction_statistics/', transaction_statistics, name='list_transaction_statistics'),
    path('all_transactions/', all_transactions, name='all_transactions'),
    path('refund_transaction/', refund_transaction, name='refund_transaction'),
]
