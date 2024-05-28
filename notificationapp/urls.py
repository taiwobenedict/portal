# howdy/urls.py
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic import TemplateView

from notificationapp.views import *

app_name='notificationapp'
urlpatterns = [
    path('all', ListNotification, name='list_alert'),
    path('<int:pk>/note', detailNotification, name='alert_detail'),
]