import requests, json
from django.utils import timezone
from django.conf import settings
import time

def prevent_doubles(request, code, number):
  # getSessionId = request.META["HTTP_COOKIE"].split(" ")[1].split("=")[1]
  userId = request.user.id
  request.session['code'] = code
  request.session['userId'] = userId
  
  try:
    if request.session.get('service_time') == None and request.session.get('number') == None and request.session['userId'] != None:
      request.session['service_time'] = timezone.now().timestamp()
      request.session['number'] = number
      return False
    else:
      time_diff = int(timezone.now().timestamp()) - int(request.session.get('service_time'))
      print("02", time_diff, settings.TIME_IN_SECONDS_INTERVAL_TO_PREVENT_DOUBLE_RECHARGE)
      if time_diff < settings.TIME_IN_SECONDS_INTERVAL_TO_PREVENT_DOUBLE_RECHARGE and request.session['userId'] == userId:
        # del request.session[service_time]
        # del request.session['number']
        # del request.session['sessionId']
        # del request.session['userId']
        return True
      else:
        print("03")
        request.session['service_time'] = timezone.now().timestamp()
        request.session['number'] = number
        request.session['userId'] = userId
        return False
  except Exception as e:
    print(e, "04")
    return True


from functools import wraps
from django.http import HttpResponseRedirect

# def preventD(function):
#   @wraps(function)
#   def wrap(request, *args, **kwargs):

#         profile = request.user.get_profile()
#         if profile.usertype == 'Author':
#              return function(request, *args, **kwargs)
#         else:
#             return HttpResponseRedirect('/')

#   return wrap