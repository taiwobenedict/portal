# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from electricity.views import *

app_name='electricityLocalView'
urlpatterns = [
    #Electricity API
    path('electricityTemplate', electricityPurchaseView, name='eletricityPurchaseTemplate'),

    path('electricityProcessPurchase/<str:code>', electricityProcessPurchaseView, name='electricityProcessPurchase'),
]