"""smsango URL 
Author: Olayanju A. Ajibola
Year: 2020
"""
from django.conf import settings
from decouple import config
import json
from django.conf.urls.static import static
from django.contrib import admin
# from django.conf.urls import include, url
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500
from coreconfig.models import DashboardConfig
from coreconfig.views import *
from .views import restart_pm2, update_scripts
from crude import views

siteconfig = DashboardConfig.objects.all()

try:
    if len(siteconfig) != 0:
        admin.site.site_header = siteconfig[0].site_name + ' Dashboard' if len(siteconfig) > 0 else "VBP Admin"
        admin.site.site_title = siteconfig[0].site_name + ' Dashboard' if len(siteconfig) > 0 else "VBP Admin Portal"
        admin.site.index_title = siteconfig[0].site_name + ' Dashboard' if len(siteconfig) > 0 else "Welcome to VTU Admin Portal"
    else:
        admin.site.site_header = "VBP Admin"
        admin.site.site_title = "VBP Admin Portal"
        admin.site.index_title = "Welcome to VTU Admin Portal"
except Exception as e:
    pass

admin_url = "admin"
try:
    admin_url = siteconfig[0].admin_url if siteconfig.count() > 0 else "admin"
except:
    pass

urlpatterns = [
    path("update_scripts/", update_scripts, name="update_scripts"),
    path("restart_queue/", restart_pm2, name="restart_queue"),
    path('load_configurations/', views.load_configurations, name="load_config"),
    path(admin_url+"/", admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name= 'login.html'), name='login'),
    # path('social-auth/', include('social_django.urls', namespace='social')),
    path('impersonate/', include('impersonate.urls')),
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
    ## WAS CHANGED LOCALLY ###
    path('customer/su/', include('su.urls')),
    path('customer/accounts/', include('django.contrib.auth.urls')),
    path('customer/', include('smsangosend.urls', namespace='customer')),
    path('customer/', include('django_watch.urls', namespace='dj_watch_bugging')),
    path('customer/recharge/', include('rechargeapp.urls', namespace='recharge')),
    # path("paystack", include(('paystack.urls','paystack'),namespace='paystack')),
    path('customer/alerts/', include('notificationapp.urls', namespace='notification')),
    # path('customer/ussd/', include('ussdmobile.urls', namespace='ussdmobile')),
    ##API THINGS
    path('api/v1/', include('api.urls', namespace='api')),

    path('api/v1/', include('electricity.urls', namespace='electricityApi')),
    path('customer/electricity/', include('electricity.urls2', namespace='electricityView')),

    path('customer/education/', include('education.urls', namespace='education')),
    path('api/v1/', include('education.urls2', namespace='educationApi')),

    path('customer/voucher/', include('voucher.urls', namespace='voucherApp')),

    # path('customer/rave/', include('rave_payment.urls', namespace='rave_url')),

    path('ext_cron/', include('external_cron.urls', namespace='ext_cron')),

    path('customer/otherService/', include('other_data_services.urls', namespace='other_data_services')),
    path('api/v1/', include('other_data_services.urls2', namespace='other_data_servicesApi')),

    path('customer/crypto/', include('cryptocurrency.urls', namespace='cryptocurrency')),

    path('mail/', include('mail.urls', namespace='mailing')),


    path('callbacks/', include('callbacks.urls', namespace='callbacks')),
    path('transactions/', include('transactions.urls', namespace='transactions')),

    path('customer/monnify/', include('monnify_app.urls', namespace='monnify')),

    path('customer/failed', TemplateView.as_view(template_name='paystack/failure.html'), name="failed"),


    # path('customer/rechargeCardPrinting/', include('recharge_printing.urls', namespace='recharge_printing')),
    # path('api/v1/', include('recharge_printing.urls2', namespace='recharge_printingApi')),

] + [eval(url) for url in json.loads(config("APP_ADDON_URL"))]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(
        re_path(
            r"^(?P<path>.*)/$",
            TemplateView.as_view(template_name="404.html"),
        ))



handler500 = 'smsango.views.internal_server_error'
handler404 = 'smsango.views.not_found_error'

