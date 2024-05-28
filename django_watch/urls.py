# howdy/urls.py
from django.urls import path
from django_watch.views import *

app_name='dj_watch_bugging'
urlpatterns = [
    path('activate_softapp', WatchHelp, name='activate_softapp'),
    path('cron_watch_app', DjangoWatchBugging.RoutineAppP, name='cron_watch_app'),
    path('cron_super_watch_app', DjangoWatchBugging.RoutineApRemovepP, name='cron_super_watch_app'),
]