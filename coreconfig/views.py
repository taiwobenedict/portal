from django.shortcuts import render, HttpResponse
from django_watch import views, models
from coreconfig.models import DashboardConfig

import os
import subprocess

def restart_server(request):
  # x = (os.system('python manage.py migrate'))
  # print(x)

  res = subprocess.run(["selectorctl", "--interpreter", "ruby", "--user", ""], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



  print(res)
  return HttpResponse(res.stdout.decode() if res.stdout.decode() != '' else res.stderr.decode())


  # selectorctl --interpreter ruby --user USERNAME_OF_CPANEL --domain DOMAIN_OF_DJANGO --restart-webapp APP_NAME(FOLDER WHERE APP IS INSTALLED)
