# howdy/urls.py
from django.urls import path, include
from external_cron.views import RunTask

app_name='ext_cron'
urlpatterns = [
    path('run_task', RunTask, name='run_task'),
]