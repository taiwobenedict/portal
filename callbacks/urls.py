# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from callbacks.views import *

app_name='callbacks'
urlpatterns = [
    path('<str:transactionId>', TransactionCallback, name='transactions_callback'),

    # path('data/callback/<str:transactionId>', CallBackDataTopUpView, name='data_callback'),

    # path('cable/callback/<str:transactionId>', CallBackCableView, name='cable_callback'),
    
    #path('electricity/callback/<str:transactionId>', AirtimeEmptyTemplate, name='elect_callback'),
]