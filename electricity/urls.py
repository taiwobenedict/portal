# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from electricity.views import *

app_name='electricity'
urlpatterns = [
    #Electricity API
    path('electricityCheck', electricityCustomerCheck.as_view(), name='apiElectricityCheck'),
    path('electricityPurchase', electricityPurchase.as_view(), name='apiElectricityPurchase'),
    path('electricityTrans', electricityTransactions.as_view(), name='apiElectricityTransactions'),

    path('electricityTemplate', electricityPurchaseView, name='eletricityPurchaseTemplate'),

    path('electricityTransactionPage', electricityTransactionsPage, name='elecTransPage'),
    path('singleElectrictyTransaction', electricityTransactionDetails.as_view(), name='singleElectrictyTransaction'),

    path('electricity/list_active', listElectricityServices, name='elec_list_active'),
]