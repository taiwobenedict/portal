# howdy/urls.py
from django.conf.urls import url
from django.urls import path
from mail.views import *

app_name='mailing'
urlpatterns = [
    path('send-mail/', sendEmailTemplate, name='send_email'),
]