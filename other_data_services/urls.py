# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from other_data_services.smile_views import SmileTransaction, smilePage
from other_data_services.mtn_sme_views import smePage
from other_data_services.spectranet_views import *
from other_data_services.intl_airtime_views import *


app_name='other_data_services'
urlpatterns = [
    #Electricity API
    path('smileTransactions', SmileTransaction, name='smileTransactions'),
    path('smile', smilePage, name='smilePage'),

    path('mtnSME', smePage, name='mtnSME'),

    path('spectranetTransaction', spectranetDTransaction, name='spectranetTransaction'),
    path('spectranetPage', spectranetPage, name='spectranetPage'),

    path('intl_airtime_page', intAirtimeView, name='intl_airtime_page'),
    path('intl_airtime_transaction', IntAirtimeDTransaction, name='int_airtime_trans'),


]