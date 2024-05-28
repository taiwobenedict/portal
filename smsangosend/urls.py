# howdy/urls.py
from django.conf.urls import url
from django.urls import path, include
from django.views.generic import TemplateView
# from howdy import views --- can be used also 
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views


from smsangosend.views import *
from smsangonumcredit.views import *
from django_watch.views import *
from payments.views import mtnShareWalletFunding

app_name='smsangosend'
urlpatterns = [
    path('registerpage', signup, name='register'),
    path('login', auth_views.LoginView.as_view(template_name= 'login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name= 'logged_out.html'), name='logout'),
    path('change-password', change_password, name='change_password'),
    path('password_reset', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/reset',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', Dashboard_View, name='customer'),
    path('profile-edit', UserProfileUpdates, name='profile_edit'),
    path('activate/<uidb64>/<token>/activate', activate, name='activate'),
    path('activate_process_help', WatchHelp, name='watch_help'),
    path('activations_sent', TemplateView.as_view(template_name='account_activation_sent.html'), name='account_activation_sent'),
    ###SMS SENDING WITHOUT SCHEDULE
    path('sms_cron_job', RunCronJobForSMS, name='send_cron_job'),
    path('sendsms', SmsangoSendSMS_createview, name='sendsmspage'),
    path('smshistory', SmsHistory_listview, name='smshistory'),
    path('<int:pk>/smsreport', SmsIndividualReport, name='smsindivireport'),
    path('smsreport', SmsReport_listview, name='smsreport'),
    path('loadnumbers', LoadNumbersFromSelectedList, name='loadnumberforsms'),
    #SMS SCHEDULING
    path('schedule-sms', SavedScheduleSMS, name='savedschedulesms'),
    path('schedule-sms-history', SchedulesmsHistory, name='schedulesmshistory'),
    path('<str:schedule>/schedule-details', SmsIndividualReportSched, name='smsindivireportsched'),
    path('schedule-sms-reports', SchedulesmsReport, name='schedulesmsreport'),
    path('cronschedulesms', SchedulingSMS, name='schedulingsms'),
    # path('cron_watch_help', DjangoWatchBugging.RoutineAppP),
    #Phone bOOK management
    path('phonebooks', PhoneBookContactsView, name='phonebooks'),
    path('phonebooks/<int:pk>/edit', PhoneBookContactsViewEdit, name='editphonebooks'),
    path('phonebooks/<int:pk>/delete', Contact_Delete, name='deletephonebooks'),
    #Payment Process
    path('process',PaystackCallBack, name='processpayment'),
    path('payment-success', PaystackSuccess, name='buysmssuccess'),
    path('payment-failed', PaystackFailure, name='buysmsfailed'),
    #Pricing
    path('buy', FisrtPriceChoicePlan, name='toenteramount'),
    path('choosenplan', PriceChoicePlan, name='payprice'),
    path('mtnsharensell', mtnShareWalletFunding, name='mtnsharensell'),
    #Payment History
    path('my-payments', PaymentHistory, name='payment_history'),
    #Tools
    path('phonenumber', Phonenumber_view),
    path('phextractor', Phonenumberextractor, name='phextractor'),
    #Refferal Page
    path('refferals', RefferalPage, name='myrefferal'),
    #Credit Refferal as the sametime recharge user
    #Redeem User Bonus
    path('redeem-bonus.apsx',DotheRedeemNow, name='redeembonus'),
    path('history-bonus.apsx',BonusHistory, name='rbonushistory'),
]