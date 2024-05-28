# howdy/urls.py
from django.conf.urls import url
from django.urls import path, include

from whatsapp_api.views import *

app_name='whatsapp_api'
urlpatterns = [
    path('whatsapp', generalPostMethod, name='whatsapp_api'),
]