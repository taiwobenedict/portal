import ast
import string

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.validators import RegexValidator
from django.db import IntegrityError, transaction

import random
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, CreateView
import re
import requests, datetime
from django.utils.crypto import get_random_string
# from datetime import 
from django.views import View
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text, smart_text 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
UserModel = get_user_model() 
from django.contrib.auth.models import User
from django.views import generic
from .forms import *
from .models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import PricingPerSMSPerUserToPurchase, DefaultPricePerSMSToPurchase
from payments.models import *
import decimal, json
from  more_itertools import unique_everseen
from django.contrib import messages
from django.utils.crypto import get_random_string
from smsangosend.signals import sendMailToUser

from celery import shared_task
from background_task import background

# @shared_task will be used for celery
@background(schedule=5, remove_existing_tasks=True)
def send_bulk_sms_bg(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, opages):
    pk = (int(userid))
    print(sender)
    status = ''
    mike = get_object_or_404(UserModel, pk=pk)
    rt = SmsangoSBulkCredit.objects.get(user=mike)
    old_balance = rt.smscredit
    print(smsroute)
    print(numcount)

    #Check if User is a Reseller or Not
    from resellers.utility import ProcessUserReseller
    is_reseller = ProcessUserReseller(mike, smsroute['apiamtpersms'], 'sms', 'sms')

    if is_reseller[1] is True:
      smsroute['apiamtpersms'] = is_reseller[0]
    else:
      pass

    numbers_to = recipients.strip()
    S1 = sender
    M  = messagecontent.strip()
    #HTTP API
    sently, notsently, sentlyy, notsentlyy, creditusedall = [], [], "", "", 0.0

    if smsroute['send_one_by_one'] is True:
      for reci in numcount:
        try:
          iurl = smsroute['url'].strip()
          iurl_data = smsroute['url_data']
          replace_keys = (("[TO]", reci),("[SENDER]", S1), ("[MESSAGE]", M))
          for (i,j) in replace_keys:
            iurl = iurl.replace(i,j)
            iurl_data = str(iurl_data).replace(i,j)
          paramet = iurl_data.replace('"', '').replace("'", '"')

          paramet = ast.literal_eval(paramet)
          
          from vbp_helper import request_method
          info = request_method.call_external_api(iurl, paramet['data'], paramet['headers'])
          print(info)
          # inf = re.compile(r'^OK')
          print("///;;;;;;;;;;;", info)
          api_respons = smsroute['api_response']
          resp = api_respons #'-13'
          if resp in str(info):
            crbalused = smsroute['apiamtpersms'] * opages
            rt.smscredit -= decimal.Decimal(crbalused)
            rt.save()
            sently.append(reci)
          else:
            notsently.append(reci)
          #Reformat the list of numbers 
        except requests.exceptions.RequestException as e:
          pass
          #Logic that Deduct and update credits     
      notsentlyy = ','.join(notsently)
      sentlyy = ','.join(sently)
      print(sently, notsently)
      if len(sently) > 0 and len(notsently) == 0:
        status = "Sent"
      elif len(sently) > 0 and len(notsently) > 0:
        status = 'Sent <i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
      elif len(sently) == 0 and len(notsently) > 0:
        status = "Not Sent" 
      creditusedall = len(sently) * smsroute['apiamtpersms'] * opages
      print(creditusedall, 'creditusedall')
      print(old_balance, 'old_balance')
    # print(creditusedall, mike, sender, numbers_to, messagecontent, notsentlyy, sentlyy, smsroute, old_balance, (old_balance - creditusedall), status)
    else:
      count_num = len(numcount)
      numcount = ",".join(numcount)
      print(numcount, "==============////////============")
      try:
        iurl = smsroute['url'].strip()
        iurl_data = smsroute['url_data']
        replace_keys = (("[TO]", numcount),("[SENDER]", S1), ("[MESSAGE]", M))
        for (i,j) in replace_keys:
          iurl = iurl.replace(i,j)
          iurl_data = str(iurl_data).replace(i,j)
        paramet = iurl_data.replace('"', '').replace("'", '"')

        paramet = ast.literal_eval(paramet)
        
        from vbp_helper import request_method
        info = request_method.call_external_api(iurl, paramet['data'], paramet['headers'])
        print(info)
        # inf = re.compile(r'^OK')
        print("///;;;;;;;;;;;", info)
        api_respons = smsroute['api_response']
        resp = api_respons #'-13'
        if resp in str(info):
          crbalused = smsroute['apiamtpersms'] * opages * count_num
          print(crbalused, "-----")
          rt.smscredit -= decimal.Decimal(crbalused)
          rt.save()
          sentlyy = numcount
          creditusedall = crbalused
          status = "Sent"
        else:
          status = "Not Sent"
          notsentlyy = numcount
        #Reformat the list of numbers 
      except requests.exceptions.RequestException as e:
        pass


    ob = SmsangoSendSMS(
      user = mike,
      reference = get_random_string(21),
      sender = sender,
      recipients = numbers_to,
      messagecontent = messagecontent,
      notsently = notsentlyy,
      sently = sentlyy,
      apiRoute = smsroute['router'],
      old_balance=float(old_balance),
      new_balance=float(old_balance) - float(creditusedall),
      status = status,
      creditusedall = creditusedall
    )
    ob.save()
    # print('sms all sent and saved successfully')
    return ('Done')

#For SMS Scheduling
@background(schedule=5, remove_existing_tasks=True)
def SendScheduledSMS_bg(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, rtcredit, scheduleidnum, opages):
    pk = (int(userid))
    status = ''
    mike = get_object_or_404(UserModel, pk=pk)
    rt = SmsangoSBulkCredit.objects.get(user=mike)
    old_balance = rt.smscredit

    #Check if User is a Reseller or Not
    from resellers.utility import ProcessUserReseller
    is_reseller = ProcessUserReseller(mike, smsroute['apiamtpersms'], 'sms', 'sms')

    if is_reseller[1] is True:
      smsroute['apiamtpersms'] = is_reseller[0]
    else:
      pass

    numbers_to = recipients.strip()
    S1 = sender
    M  = messagecontent
    #HTTP API
    sently, notsently, sentlyy, notsentlyy, creditusedall = [], [], "", "", 0.0
    if smsroute['send_one_by_one'] is True:
      for reci in numcount:
        try:
          iurl = smsroute['url'].strip()
          iurl_data = smsroute['url_data']
          replace_keys = (("[TO]", reci),("[SENDER]", S1), ("[MESSAGE]", M))
          for (i,j) in replace_keys:
            iurl = iurl.replace(i,j)
            iurl_data = str(iurl_data).replace(i,j)
          paramet = iurl_data.replace('"', '').replace("'", '"')

          paramet = ast.literal_eval(paramet)
          
          from vbp_helper import request_method
          info = request_method.call_external_api(iurl, paramet['data'], paramet['headers'])
          print(info)
          # inf = re.compile(r'^OK')
          print("///;;;;;;;;;;;", info)
          api_respons = smsroute['api_response']
          resp = api_respons #'-13'
          if resp in str(info):
            crbalused = smsroute['apiamtpersms'] * opages
            rt.smscredit -= decimal.Decimal(crbalused)
            rt.save()
            sently.append(reci)
          else:
            notsently.append(reci)
          #Reformat the list of numbers 
        except requests.exceptions.RequestException as e:
          pass
          #Logic that Deduct and update credits     
      notsentlyy = ','.join(notsently)
      sentlyy = ','.join(sently)
      print(sently, notsently)
      if len(sently) > 0 and len(notsently) == 0:
        status = "Sent"
      elif len(sently) > 0 and len(notsently) > 0:
        status = 'Sent <i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
      elif len(sently) == 0 and len(notsently) > 0:
        status = "Not Sent" 
      creditusedall = len(sently) * smsroute['apiamtpersms'] * opages
      print(creditusedall, 'creditusedall')
      print(old_balance, 'old_balance')
    # print(creditusedall, mike, sender, numbers_to, messagecontent, notsentlyy, sentlyy, smsroute, old_balance, (old_balance - creditusedall), status)
    else:
      count_num = len(numcount)
      numcount = ",".join(numcount)
      print(numcount, "==============////////============")
      try:
        iurl = smsroute['url'].strip()
        iurl_data = smsroute['url_data']
        replace_keys = (("[TO]", numcount),("[SENDER]", S1), ("[MESSAGE]", M))
        for (i,j) in replace_keys:
          iurl = iurl.replace(i,j)
          iurl_data = str(iurl_data).replace(i,j)
        paramet = iurl_data.replace('"', '').replace("'", '"')

        paramet = ast.literal_eval(paramet)
        
        from vbp_helper import request_method
        info = request_method.call_external_api(iurl, paramet['data'], paramet['headers'])
        print(info)
        # inf = re.compile(r'^OK')
        print("///;;;;;;;;;;;", info)
        api_respons = smsroute['api_response']
        resp = api_respons #'-13'
        if resp in str(info):
          crbalused = smsroute['apiamtpersms'] * opages * count_num
          print(crbalused, "-----")
          rt.smscredit -= decimal.Decimal(crbalused)
          rt.save()
          sentlyy = numcount
          creditusedall = crbalused
          status = "Sent"
        else:
          status = "Not Sent"
          notsentlyy = numcount
        #Reformat the list of numbers 
      except requests.exceptions.RequestException as e:
        pass
    gettime = SavedScheduledSMS.objects.get(scheduleidnum=scheduleidnum).time_to_send
    obj = SmsangoSendSMS.objects.create(
      user = mike,
      sender = sender,
      recipients = recipients,
      messagecontent = messagecontent,
      notsently = notsentlyy, #list of not sent numbers 
      sently = sentlyy, #list of sent numbers
      apiRoute = smsroute['router'],
      time_to_send=gettime,
      status = status,
      creditusedall = creditusedall,
      old_balance=float(old_balance),
      new_balance=float(old_balance) - float(creditusedall),
      scheduleidnum = scheduleidnum
    )
    print('saved ...')
    updatesavedschedulestatus = SavedScheduledSMS.objects.get(scheduleidnum=scheduleidnum)
    updatesavedschedulestatus.status = True
    updatesavedschedulestatus.save()
    print('finally saved')			
    return HttpResponse ('Job Completed')

def sendTheMail(sender, **kwargs):
  try:
    user = kwargs['user']
    subject = kwargs['subject']
    message = kwargs['message']
    user.email_user(subject, message)
    print('Done Sent')
    return 'done'
  except Exception as e:
    print(e)
    print('sending failed')
    return 'Sending Failed'

sendMailToUser.connect(sendTheMail)


