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
import decimal
from  more_itertools import unique_everseen
from django.contrib import messages
from django.utils.crypto import get_random_string

from celery import shared_task

@shared_task
def send_bulk_sms_bg(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, rtcredit, oto, router, apiamtpersms):
    pk = (int(userid))
    print(sender)
    mike = get_object_or_404(UserModel, pk=pk)
    messgcontentlength = len(messagecontent)
    if messgcontentlength < 161:
        opages = 1
    elif messgcontentlength > 160 and messgcontentlength < 321:
        opages = 2
    elif messgcontentlength > 320 and messgcontentlength < 481:
        opages = 3
    rt = SmsangoSBulkCredit.objects.get(user=mike)
    if smsroute == "DND":
        sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
        for i in sendwithdnd:
            oto = i.apurl
            apiamtpersms = i.apiamtpersms
            router = "DND ROUTE"
            # print ("send with dnd" + oto )
    else:
        sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
        # print(sendwithnotdnd)
        for i in sendwithnotdnd:
            oto = i.apurl
            apiamtpersms = i.apiamtpersms
            router = "NON DND ROUTE"
            # print ("send without dnd" + oto )            
    numcount = recipients.split(',')
    S1 = sender
    PN = recipients
    M  = messagecontent.strip()
    #HTTP API
    sently = []
    notsently = []
    status = ''
    for reci in numcount:
        try:
            iurl = oto
            url1 = iurl.replace("[TO]", reci)
            urlt = url1.replace ("[SENDER]", S1)
            apiurl = urlt.replace ("[MESSAGE]", M)
            r = requests.post(apiurl)
            info = (r.content).decode("utf-8")
            inf = re.compile(r'^OK')
            # mo = inf.search(info)
            api_respons = APIUrl.objects.filter(is_active=True)
            for ed in api_respons:
                    ed_api = ed.api_response
            resp = ed_api#'-13'
            # print (resp)
            if not resp in info:
                if len(notsently) == 1:
                    successde = """Message Not Sent Check <a href='/sms/customer/smshistory'>SMS Report</a> for full details"""
                    status = "Not sent"
                else:
                    successde = "Some messages were not sent Check <a href='/sms/customer/smshistory'>SMS Report</a> for full details"
                    status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
                notsently.append(reci)
            else:
                if len(notsently) == 0:
                    successdety = "Message Sent Successfully Check <a href='/sms/customer/smshistory'>SMS Report</a> for full details"
                    status = "Sent"
                    # status.append(status)
                else:
                    successdety = "Some messages were not sent Check <a href='/sms/customer/smshistory'>SMS Report</a> for full details"
                    status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
                sently.append(reci)
            #Reformat the list of numbers 
        except requests.exceptions.RequestException as e:
            successdety = 'something went wrong'
            #Logic that Deduct and update credits   
    with transaction.atomic():              
        crbalused = (len(sently) * apiamtpersms * opages)
        xcredit = float(rt.smscredit) - float(crbalused)
        rt.smscredit = xcredit
        rt.save()
    notsentlyy = ','.join(notsently)
    sentlyy = ','.join(sently)
    if sently and not notsently:
        status = "Sent"
    elif sently and notsently:
        status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
    elif notsently and not sently:
        status = "Not Sent" 
    creditusedall = len(sently) * apiamtpersms * opages
    print(creditusedall)
    with transaction.atomic():
        obj = SmsangoSendSMS.objects.create(
            user = (mike),
            sender = sender,
            recipients = recipients,
            messagecontent = messagecontent,
            notsently = notsentlyy, #list of not sent numbers 
            sently = sentlyy, #list of sent numbers
            apiRoute = router,
            status = status,
            creditusedall = creditusedall
        )
        return ('Done')

#For SMS Scheduling
@shared_task
def SendScheduledSMS_bg(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, rtcredit, scheduleidnum):
    pk = (int(userid))
    mike = get_object_or_404(UserModel, pk=pk)
    print(mike)
    messgcontentlength = len(messagecontent)
    if messgcontentlength in range(1, 160):
        opages = 1
    elif messgcontentlength in range(161, 320):
        opages = 2
    elif messgcontentlength in range(321, 480):
        opages = 3
    print(opages)
    rt = SmsangoSBulkCredit.objects.get(user=mike)
    if smsroute == "DND":
        sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
        for i in sendwithdnd:
            oto = i.apurl
            apiamtpersms = i.apiamtpersms
            router = "DND ROUTE"
            # print ("send with dnd" + oto )
    else:
        sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
        print(sendwithnotdnd)
        for i in sendwithnotdnd:
            oto = i.apurl
            apiamtpersms = i.apiamtpersms            
            router = "NON DND ROUTE"
            # print ("send without dnd" + oto )
    numcount = recipients.split(',')
    S1 = sender
    PN = recipients
    M  = messagecontent
    #HTTP API
    sently = []
    notsently = []
    for reci in numcount:
        try:
            iurl = oto
            url1 = iurl.replace("[TO]", reci)
            urlt = url1.replace ("[SENDER]", S1)
            apiurl = urlt.replace ("[MESSAGE]", M)
            r = requests.post(apiurl)
            info = (r.content).decode("utf-8") 
            api_respons = APIUrl.objects.filter(is_active=True)
            for ed in api_respons:
                    ed_api = ed.api_response
            resp = ed_api
            # print (resp)
            if not resp in info:
                if len(notsently) == 1:
                    successde = "Message Not Sent Check <a href='/customer/smsreport/'>SMS Report</a> for full details"
                    status = "Not sent"
                else:
                    successde = "Some messages were not sent Check <a href='/customer/smsreport/'>SMS Report</a> for full details"
                    status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
                # print(successde)
                notsently.append(reci)
            else:
                if len(notsently) == 0:
                    successdety = "Message Sent Successfully Check <a href='/customer/smsreport/'>SMS Report</a> for full details"
                    status = "Sent"  							
                else:
                    successdety = "Some messages were not sent Check <a href='/customer/smsreport/'>SMS Report</a> for full details"
                    status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
                sently.append(reci)

                # print(loall)

            #Reformat the list of numbers 
        except requests.exceptions.RequestException as e:
            successdety = 'something went wrong'
            return HttpResponse ('Peoblems Completed')

    #Logic that Deduct and update credits 
    with transaction.atomic():                  
        crbalused = (len(sently) * apiamtpersms * opages)
        rt.smscredit -= crbalused
        rt.save()
    notsentlyy = ','.join(notsently)
    sentlyy = ','.join(sently)
    if sently and not notsently:
        status = "Sent"
    elif sently and notsently:
        status = "Sent <span class='glyphicon glyphicon-exclamation-sign' aria-hidden='true'></span>"
    elif notsently and not sently:
        status = "Not Sent" 
    creditusedall = len(sently) * apiamtpersms * opages
    print(creditusedall)
    print(sently)
    print(notsently)
    with transaction.atomic():
        gettime = SavedScheduledSMS.objects.get(scheduleidnum=scheduleidnum).time_to_send
        obj = ScheduleSendSMS.objects.create(
            user = mike,
            sender = sender,
            recipients = recipients,
            messagecontent = messagecontent,
            notsently = notsentlyy, #list of not sent numbers 
            sently = sentlyy, #list of sent numbers
            apiRoute = router,
            time_to_send=gettime,
            status = status,
            creditusedall = creditusedall,
            scheduleidnum = scheduleidnum
        )
        print('saved ...')
        updatesavedschedulestatus = SavedScheduledSMS.objects.get(scheduleidnum=scheduleidnum)
        updatesavedschedulestatus.status = True
        updatesavedschedulestatus.save()
        print('finally saved')			
        return HttpResponse ('Job Completed')