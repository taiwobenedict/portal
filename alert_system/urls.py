# howdy/urls.py
from django.conf.urls import url
from django.urls import path
from alert_system.views import *

app_name='alert_system'
urlpatterns = [
    path('alert_system/<int:pk>', process_read_alert, name='process_alert'),
    path('turorial_news', tutorial_news, name='news'),
]