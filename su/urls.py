
from django.conf.urls import url
from django.urls import path

from su.views import switch_user, ListAllUserToSwitch #switch_user

app_name = 'su'
urlpatterns = [
  path('<username>/user', switch_user, name="su_switch_user"),
  path('users', ListAllUserToSwitch, name="list_all_users"),
]
