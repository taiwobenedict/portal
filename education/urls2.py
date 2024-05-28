# howdy/urls.py
from django.conf.urls import url
from django.urls import include, path

from education.views import *

app_name='educationView'
urlpatterns = [
    #Electricity API
    path('resultCheckers', ResultCheckerView.as_view(), name='resultCheckers'),
    path('getPinDetails', GetPinDetails.as_view(), name='getPinDetails'),
]