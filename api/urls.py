# howdy/urls.py
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic import TemplateView

from api.views import *
from api.views2 import (PaymentForMobileApi,PaystackCallBack,CheckActiveDataApi,
AirtimeTransactionAPI,DataTransactionAPI,CableTransactionAPI, CableTransactionDetailedAPI, PayStackTransactionAPI, RefferalPageAPI,
DoTheRedeemNowAPI,BonusPageAPI,notificationsApi,readNotificationsApi, TransactionAPI)
from api.views3 import (SmsangoSendSMSApi, smsHistoryApi, singleSmsHistoryApi, DoKycVerification)
from api.views4 import KYCVerificationTemplate

app_name='api'
urlpatterns = [
    path('test', HelloView.as_view(), name='test'),
    path('tested', Test.as_view(), name='tested'),
    path('signup', apiSignup.as_view(), name='apisignup'),
    path('login', apiLogin.as_view(), name='apilogin'),
    path('passwordreset', apiPasswordReset.as_view(), name='apiPasswordReset'),
    path('profileupdate', apiProfileUpdate.as_view(), name='apiProfileUpdate'),
    path('profileview', apiGetUserProfile.as_view(), name='apiProfileView'),
    path('userdetails', apiGetUserDetails.as_view(), name='apiuserdetails'),
    path('userref', RefferalPageAPI.as_view(), name='apiUserRef'),
    path('userredeembonus', DoTheRedeemNowAPI.as_view(), name='apiRedeemBonus'),
    path('refbonus', BonusPageAPI.as_view(), name='apiRefBonus'),
    path('activedataapi', CheckActiveDataApi.as_view(), name='activedataapi'),
    path('payment-api', PaymentForMobileApi.as_view(), name='paymentapi'),
    path('payment-process-api', PaystackCallBack.as_view(), name='paymentproccess'),
    path('paystacktransaction', PayStackTransactionAPI.as_view(), name='api_paystack_tran'),
    path('generate-token', CreateApiToken, name='generate_token'),
    path('verify-domain', verifyDomain, name='verify_domain'),
    path('add-domain', UpdateDomain, name='update_domain'),


    path('balance', ApiBalance.as_view(), name='api_balance'),
    path('airtime', ApiAirtimeView.as_view(), name='api_airtime'),
    path('airtimetransaction', AirtimeTransactionAPI.as_view(), name='api_airtime_tran'),
    path('data', ApiDataView.as_view(), name='api_data'),
    path('datatransaction', DataTransactionAPI.as_view(), name='api_data_tran'),
    path('check-cable-customer', ApiCheckCustomer.as_view(), name='api_data'),
    path('cable', ApiCableRecharge.as_view(), name='api_cable'),
    path('cable-plans', listCableTv, name='cable_plans'),
    path('cable-plans-tv', listCableTvs, name='cable_plans'),
    path('cabletransaction', CableTransactionAPI.as_view(), name='api_cable_tran'),
    path('cabletransactiondetails', CableTransactionDetailedAPI.as_view(), name='api_cable_tran_details'),
    path('cable_plan_list', listCablePlans, name='cable_plan_list'),
    path('notificationapi', notificationsApi.as_view(), name='api_notification'),
    path('readnotificationapi', readNotificationsApi.as_view(), name='api_notification'),
    #SMS API ROUTE
    path('sendsmsapi', SmsangoSendSMSApi.as_view(), name='smsangoSendApi'),
    path('sendhistoryapi', smsHistoryApi.as_view(), name='smsHistoryApi'),
    path('sendsinglehistoryapi', singleSmsHistoryApi.as_view(), name='smsSingleHistoryApi'),
    path('transaction-api', TransactionAPI.as_view(), name='transaction_api'),
    path('kyc-verification', DoKycVerification.as_view(), name='dokycverification'),
    path('kyc-template', KYCVerificationTemplate.as_view(), name='kyc_template'),
]