# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from other_data_services.smile_views import smileTransactions, PurchaseSmile, CheckSmileNo
from other_data_services.mtn_sme_views import PurchaseSme
from other_data_services.spectranet_views import PurchaseSpectranet, spectranetDTransactions
from other_data_services.views import *
from other_data_services.intl_airtime_views import *

app_name='other_data_servicesApi'
urlpatterns = [
    #Electricity API
    path('checkSmileNo', CheckSmileNo.as_view(), name='checkSmile'),
    path('purchaseSmile', PurchaseSmile.as_view(), name='purchaseSmile'),
    path('smileTransactionsApi', smileTransactions.as_view(), name='smileTransactionApi'),

    path('purchaseSme', PurchaseSme.as_view(), name='purchaseSme'),

    path('purchaseSpectranet', PurchaseSpectranet.as_view(), name='purchaseSpectranet'),
    path('spectranetTransactionsApi', spectranetDTransactions.as_view(), name='spectranetTransactionApi'),

    path('getDetailsTransactions', GetDetailsTransactions.as_view(), name='getDetailTransactions'),

    #International Airtime
    path('verify_intl_number', CheckIntNumber.as_view(), name='check_int_number'),
    path('purchase_intl_number', PurchaseIntAirtime.as_view(), name='purchase_int_number'),
    path('intl_number_transaction', IntAirtimeDTransactions.as_view(), name='purchase_int_number'),
]