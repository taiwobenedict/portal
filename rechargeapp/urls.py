# howdy/urls.py
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic import TemplateView

from rechargeapp.views import *
from rechargeapp.cable_view import *


#urlpatterns = [
 #   path('$', views.HomePageView.as_view()),
 #   path('daabout/$', views.AboutPageView.as_view()),
 #   path('about/$', views.About.as_view()),
 #   path('contact/$', views.Contact.as_view()), # Add this /about/ route
#]
app_name='rechargeapp'
urlpatterns = [
    path('balance', CheckApiBalance, name='balance'),
    #Purchase and Payment for Airtime PayStack 
    path('airtime', AirtimeEmptyTemplate, name='airtimetemplate'),
    path('airtime_process/<str:code>', AirtimeProcessTemplate, name='airtimeprocess'),
    path('airtime-topup', AirtimeView, name='airtimetopup'),
    path('airtime-payment', AtmAirtimePaystack, name='paymentairtimetpup'),
    path('airtime-transactions', AirtimeTransaction, name='airtime_transactions'),
    #Purchase and Payment for Data Paystack DataTopView
    # path('airtime', DataEmptyTemplate, name='datatemplate'),
    path('datatopup', DataTopView, name='datatemplate'),
    path('datatopup_process/<str:code>', DataProcessTemplate, name='datatemplate_process'),
    path('databundle-topup', DataTopUpView, name='datatopup'),
    path('data-payment', AtmDataPaystack, name='paymentdatatpup'),
    path('data-transactions', DataTransaction, name='data_transactions'),
    path('data-returnurl', ReturnUrl, name='data_return'),

    path('cable-template', cableTemplate, name='cabletvtemplate'),
    path('select-cabletv/<str:code>', selectBillAndPackage, name='cabletv'),
    path('check-customer-cabletv', Check_Customer, name='customer_check'),
    path('subscribe-cabletv', SubscribeCable, name='subscribecable'),
    path('cable-transactions', CableTransaction, name='cable_transactions'),
]