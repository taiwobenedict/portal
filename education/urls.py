# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from education.views import *

app_name='education'
urlpatterns = [
    #Electricity API
    path('educationTransactions', PinTransaction, name='educationTransactions'),
    path('educationPurchase', PinPurchaseView, name='educationPurchase'),
    path('educationProcessPurchase/<str:code>', PinProcessVeiw, name='educationProcessPurchase'),
]