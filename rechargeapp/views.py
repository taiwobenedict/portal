import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import RegexValidator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView

import datetime
import random
import re
from re import template

import json
from django.contrib.auth.models import User
from payments.models import *
from rechargeapp.models import DataNetworks, RechargeAirtimeAPI, AirtimeTopup,\
  CableRecharge, DataPlansPrices, BonusAccount, MtnDataShare
from rechargeapp.utility import get_or_none
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.views import *
from smsangonumcredit.models import BonusesPercentage
from decimal import *
from vbp_helper.helpers import evalResponse, deleteSessions, setSessions, timezoneshit
from django_ratelimit.decorators import ratelimit
from vbp_helper import prevent_double
import ast
from django.db import transaction


UserModel = get_user_model()
# Create your views here.

@login_required(login_url=settings.LOGIN_URL)
def CheckApiBalance(request):
    template_name = ""
    checkapibalance = ''
    chkbalance = requests.post(checkapibalance)
    resp = (chkbalance.content).decode("utf-8")
    return HttpResponse(resp)

@login_required(login_url=settings.LOGIN_URL)
def AirtimeEmptyTemplate(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')
  template_name = "general/general_layout.html"
  api_obj = RechargeAirtimeAPI.objects.filter(is_active=True)
  return render(request, template_name, {'products':api_obj, 'title': "Airtime", 'link': '/customer/recharge/airtime_process'})

@login_required(login_url=settings.LOGIN_URL)
def AirtimeProcessTemplate(request, code):
  template_name = "airtime/airtime_purchase_template.html"
  obj = RechargeAirtimeAPI.objects.filter(is_active=True, identifier=code)
  if len(obj) > 0:
    return render(request, template_name, {'code': code , 'obj': obj[0]})
  messages.error(request, "Something is WRONG, contact the admin for resolution")
  return render(request, template_name, {})

from django.views.decorators.cache import cache_control, never_cache
import random, time

@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@transaction.atomic
def AirtimeView(request):
    from transactions.models import Transactions
    user = request.user
    if not user.userprofile.phone:
        messages.success(request, 'Update your profile to proceed')
        return HttpResponseRedirect('/customer/profile-edit')
    if request.method == "POST":          
        network = request.POST.get('network')
        code = request.POST.get('code')
        phone = (request.POST.get('phone')).strip()
        amt = request.POST.get('amt')
        amt = abs(int(amt))
        if float(amt) > float(user.smsbulkcredit.smscredit) or int(user.smsbulkcredit.smscredit) <= 0 or float(amt) <= 0:
          messages.error(request, "Insufficient funds")
          return redirect(reverse('rechargeapp:airtimetemplate'))
        else:
          api_obj = get_or_none(RechargeAirtimeAPI, is_active=True, identifier=code)
          if api_obj == None:
            return HttpResponseRedirect('/customer/failed')

          smsbal = user.smsbulkcredit
          old_balance = smsbal.smscredit
          get_amt = (float(amt) - (float(amt) * float(api_obj.user_discount)))

          from resellers.utility import ProcessUserReseller
          is_reseller = ProcessUserReseller(user, float(amt), 'airtime', api_obj.identifier)

          if is_reseller[1] is True:
            get_amt = is_reseller[0]

          smsbal.smscredit -= Decimal(float(get_amt))
          smsbal.save()

          obj = Transactions.objects.create(
            user = user,
            bill_type = "AIRTIME",
            bill_code = code,
            bill_number = phone,
            identifier = code,
            actual_amount = amt,
            paid_amount = get_amt,
            old_balance = old_balance,
            new_balance = user.smsbulkcredit.smscredit,
            status = "QUEUE",
            reference = timezoneshit(),
            api_id = api_obj.id,
            mode = "DIRECT"
          )
          messages.success(request, "Request has been submitted")
          return redirect('rechargeapp:airtimetemplate')
    else:
      return HttpResponseRedirect('/customer/failed')

@transaction.atomic
def ProcessAirtimePurchase(object_id):
    from transactions.models import Transactions
    t = Transactions.objects.get(id=object_id, status="QUEUE")
    #t.status = "PROCESSING"
    #t.save()()
    api_obj = get_or_none(RechargeAirtimeAPI, id=t.api_id, is_active=True)
    if api_obj is None:
        t.comment = "api not activated, contact the admin"
        t.status = "FAILED"
        t.save()
        return ""
    user = t.user
    discount = float(api_obj.user_discount)
    smsbal = user.smsbulkcredit
    old_balance = smsbal.smscredit
    bonuscre = BonusAccount.objects.get(user=user)
    amt = t.actual_amount

    #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
    get_amt = float(int(amt) - (float(amt) * (discount)))

    if int(user.smsbulkcredit.smscredit) != int(t.new_balance) and t.mode != "API":
      t.status = "FAILED"
      t.comment = "Fraud Detected"
      t.save()
      return "Done"

    else:
      getApiUrl = api_obj.api_url
      getApiUrlData = api_obj.api_url_data
      network = []
      replace_keys = (('[phone]',t.bill_number), ('[amt]',str(int(amt))), ('[ordernumber]', t.reference), ('[PHONE]',t.bill_number), ('[AMT]',str(amt)), ('[ORDERNUMBER]', t.reference))
      print(replace_keys, "replace_keys")
      for (i,j) in replace_keys:
          getApiUrl = getApiUrl.replace(i,j)
          getApiUrlData = str(getApiUrlData).replace(i,j)

      # print(getApiUrlData)
      paramet = ast.literal_eval(getApiUrlData)

      print(paramet['data'])


      #Process if User is Reseller
      from resellers.utility import ProcessUserReseller
      is_reseller = ProcessUserReseller(user, float(amt), 'airtime', t.identifier)


      from vbp_helper import request_method
      info = request_method.call_external_api(getApiUrl, paramet['data'], paramet['headers'])
      print(info)

      if any(respo in str(info) for respo in api_obj.success_code.split(",")):
          t.api_response = info
          t.status = "SUCCESS"
          t.save()

          if is_reseller[1] is True:
            bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
            if not bonus_to_add is None:
                try:
                  getbonus_amt = GetBonusAmtToCredit(bonus_to_add, 'purchase_airtime_bonus', api_obj.identifier) 
                  bonuscre.bonus += Decimal(getbonus_amt * int(amt))
                  bonuscre.save()
                  getrefbonus_percent = GetBonusAmtToCredit(bonus_to_add, 'referral_airtime_bonus', api_obj.identifier)
                  getrefbonus_amt = Decimal(getrefbonus_percent * int(amt))
                  CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
                except:
                  pass

      else:
          smsbal.smscredit += Decimal(float(get_amt))
          smsbal.save()

          t.api_response = info
          t.status = "FAILED"
          t.paid_amount = 0.0
          t.new_balance = float(smsbal.smscredit)
          t.save()

          print(t.reference, "%%%%%%%", "Failed")

          from api_errors.views import ReturnErrorResponse
          resp = ReturnErrorResponse(info, api_obj.api_name, 'Recharge Was Not Successful')

    if t.callback_url:
      request_method.call_external_api(t.callback_url, {"status": t.status}, {}) 

def AtmAirtimePaystack(request):
    user = request.user
    ordernumber = request.POST.get('paystack-trxref')
    # reference = request.POST.get('reference')
    amt = request.POST.get('amount')
    phone = request.POST.get('phone')
    network = request.POST.get('network')
    #Using ATM/BANK ==> PAYSTACK PROCEDURE SO AFTER PAYMENT ACCESS THE API TO RECHARGE USER 
    if ordernumber:
        airtimeapi = 'h'+network+'&phone='+phone+'&amt='+amt
        r = requests.post(airtimeapi)
        info = (r.content).decode("utf-8")
        #checking the API repsonse
        if '100' in info:
            obj_1 = AirtimeTopup.objects.create(
                user = user,
                ordernumber = ordernumber,
                recharge_amount = int(amt)/100,
                recharge_number = phone,
                recharge_network = network,
                status = "SUCCESS",
            )
            return render(request, 'airtime/successful_recharge_card.html')
        else:
            obj_1 = AirtimeTopup.objects.create(
                user = user,
                ordernumber = ordernumber,
                recharge_amount = int(amt)/100,
                recharge_number = phone,
                recharge_network = network,
                status = "NOT SUCCESSFUL",
            )            
            return render(request, 'paystack/failure.html')
    else:
        return render(request, 'paystack/failure.html')


def GetTheDataValuesANDSplit():
  get_active_api = get_or_none(DataNetworks, is_active=True)
  if get_active_api != None:
    oyaSplit = get_active_api.network_data_amount_json.split('/')
    # print(oyaSplit)
    dataNet = {}
    for x in oyaSplit:
        equalToSplit = x.split("=")
        # print(equalToSplit)
        dataNet[equalToSplit[0].lower()] = equalToSplit[1].strip().split(',')
    # print('dataNet ==>', dataNet)
    return dataNet
  else:
    return {}


@login_required(login_url=settings.LOGIN_URL)
def DataTopView(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')
  template_name = "general/general_layout.html"
  api_obj = DataNetworks.objects.filter(is_active=True)
  return render(request, template_name, {'products':api_obj, 'title': "Data TopUp", 'link': '/customer/recharge/datatopup_process'})

@login_required(login_url=settings.LOGIN_URL)
def DataProcessTemplate(request, code):
  template_name = "datatopup/datatopup_purchase_template.html"
  obj = DataNetworks.objects.filter(is_active=True, identifier=code)
  items = []
  if len(obj) > 0:
    toJson = obj[0].network_data_amount_json.split(',')
    print(toJson)
    for i in toJson:
      print(i)
      item = {}
      x = i.split('|')
      
      item['api_amount'] = x[0]
      item['data_amount'] = x[1]
      item['urlvariable'] = x[2]
      item['what_user_sees'] = x[3]
      try:
        item['extra_variable'] = x[4]
      except:
        pass
      
      items.append(item)
    return render(request, template_name, {'code': code , 'obj': obj[0], 'items': items})
  messages.error(request, "Something is WRONG, contact the admin for resolution")
  return render(request, template_name, {'code': code , 'obj': obj, 'items': items})


def GetPrice(data_network, data_size, data_amount):
  try:
    dataNet = GetTheDataValuesANDSplit()
    dataSizeSplit = data_size.split("|")
    dSS1, dSS2, xs = dataSizeSplit[0], dataSizeSplit[1], []
    getNetworkCode, getplancd = {}, {}
    for x in dataNet[data_network.lower()]:
      get_x = x.split('|')
      if dSS1 == get_x[0] or dSS1 == get_x[1] or dSS1 == get_x[2] or dSS1 == get_x[3] or dSS1 == get_x[4]:
        if dSS2 == get_x[0] or dSS2 == get_x[1] or dSS2 == get_x[2] or dSS2 == get_x[3] or dSS2 == get_x[4]:
          xs.append(x)
          getplancd['otplan_code'] = x
    getOtherParam = getplancd['otplan_code'].split('|')
    return getOtherParam
  except Exception as e:
    return 'error'


@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@transaction.atomic
def DataTopUpView(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')

  if request.method == "POST":
    data_network = request.POST.get('network')
    code = request.POST.get('code')
    data_number = (request.POST.get('phone')).strip()
    data_size = request.POST.get('amt')
    # if prevent_double.prevent_doubles(request, code, data_number):
    #   messages.error(request, 'Transaction error this seems to be a duplicate request else retry in a minute')
    #   return redirect(reverse('rechargeapp:datatemplate'))

    split_amt = data_size.strip().split('|')
    api_amt_plan = split_amt[0]
    data_amount = split_amt[1]
    # use_credit = request.POST.get('usecredit')
    smsbal = SmsangoSBulkCredit.objects.get(user=user)
    old_balance = smsbal.smscredit
    bonuscre = BonusAccount.objects.get(user=user)
    dataapi = get_or_none(DataNetworks, is_active=True, identifier=code)
    if dataapi == None:
      return render(request, 'paystack/failure.html')
    if data_size not in dataapi.network_data_amount_json:
      messages.error(request, "Fraud detected")
      return redirect(reverse('rechargeapp:datatemplate'))

    if float(data_amount) > float(user.smsbulkcredit.smscredit) or int(user.smsbulkcredit.smscredit) <= 0 or float(data_amount) <= 0:
      messages.error(request, "Insufficient funds")
      return redirect(reverse('rechargeapp:datatemplate'))

    from transactions.models import Transactions
    from resellers.utility import ProcessUserReseller
    is_reseller = ProcessUserReseller(user, float(data_amount), 'data', code, split_amt[3])

    if is_reseller[1] is True:
      data_amount = is_reseller[0]

    smsbal.smscredit -= Decimal(float(data_amount))
    smsbal.save()

    Transactions.objects.create(
        user = user,
        bill_type = "DATA",
        bill_code = data_size.strip(),
        bill_number = data_number,
        identifier = code,
        actual_amount = data_amount,
        old_balance = old_balance,
        new_balance = smsbal.smscredit,
        reference = timezoneshit(),
        paid_amount = data_amount,
        status = "QUEUE",
        api_id = dataapi.id,
        mode = "DIRECT"
    )

    #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
    messages.success(request, 'Request submitted successful')
    return HttpResponseRedirect(reverse('rechargeapp:datatemplate'))
  return HttpResponseRedirect(reverse('rechargeapp:datatemplate'))

@transaction.atomic
def ProcessDataPurchase(object_id):
    from transactions.models import Transactions
    t = Transactions.objects.get(id=object_id, status="QUEUE")
    #t.status = "PROCESSING"
    #t.save()()
    dataapi = get_or_none(DataNetworks, id=t.api_id, is_active=True)
    if dataapi is None:
        t.comment = "api not activated, contact the admin"
        t.save()
        return ""
    user = t.user
    ordernumber = t.reference
    smsbal = SmsangoSBulkCredit.objects.get(user=user)
    old_balance = smsbal.smscredit
    bonuscre = BonusAccount.objects.get(user=user)
    code = t.identifier
    split_amt = t.bill_code.split("|")
    api_amt_plan = split_amt[0]
    data_amount = split_amt[1]
    extra_variable = ""

    try:
      extra_variable = split_amt[4]
    except Exception as e:
      pass

    #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
    if int(user.smsbulkcredit.smscredit) != int(t.new_balance) and t.mode != "API" :
      t.status = "FAILED"
      t.comment = "Fraud Detected"
      t.save()
      return "Done"

    else:
      getApiUrl = dataapi.api_url
      getApiUrlData = dataapi.api_url_data
      replace_keys = (('[phone]',t.bill_number),\
        ('[dataplan]', api_amt_plan), ('[apiamount]',api_amt_plan), ('[urlvariable]', split_amt[2]),\
          ('[ordernumber]', ordernumber), ('[PHONE]', t.bill_number),\
        ('[DATAPLAN]', api_amt_plan), ('[APIAMOUNT]', api_amt_plan), ('[URLVARIABLE]', split_amt[2]),\
          ('[ORDERNUMBER]', ordernumber), ('[EXTRAVARIABLE]', extra_variable), ('[extravariable]', extra_variable))
      for (i,j) in replace_keys:
        getApiUrl = getApiUrl.replace(i,j)
        getApiUrlData = str(getApiUrlData).replace(i,j)
      paramet = ast.literal_eval(getApiUrlData)
      # print(getApiUrl)

      from resellers.utility import ProcessUserReseller
      is_reseller = ProcessUserReseller(user, float(data_amount), 'data', code, split_amt[3])

      from vbp_helper import request_method
      info = request_method.call_external_api(getApiUrl, paramet['data'], paramet['headers'])
      print(info)
      
      print("--->", info)
      if any(respo in str(info) for respo in dataapi.success_code.split(",")):
        t.api_response = info
        t.bill_code = split_amt[2]
        t.status = "SUCCESS"
        t.save()

        if not is_reseller[1]:
          bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
          if bonus_to_add is None:
            pass
          else:
            try:
              getbonus_amt = GetBonusAmtToCredit(bonus_to_add, 'purchase_data_bonus', dataapi.identifier)
              bonuscre.bonus += Decimal(getbonus_amt * float(data_amount))
              bonuscre.save()
              getrefbonus_percent =  GetBonusAmtToCredit(bonus_to_add, 'referral_data_bonus', dataapi.identifier)
              getrefbonus_amt = Decimal(getrefbonus_percent * float(data_amount))
              CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
            except:
              pass
      else:

        smsbal.smscredit += Decimal(is_reseller[0] if is_reseller[1] else data_amount)
        smsbal.save()

        t.api_response = info
        t.paid_amount = 0.0
        t.status = "FAILED"
        t.bill_code = split_amt[2]
        t.new_balance = float(smsbal.smscredit)
        t.save()

        from api_errors.views import ReturnErrorResponse
        resp = ReturnErrorResponse(info, dataapi.api_name, 'Recharge Was Not Successful \n Try again later')

    if t.callback_url:
      request_method.call_external_api(t.callback_url, {"status": t.status}, {}) 
       

def ReturnUrl(request):
  try:
    status = request.GET['status']
    beneficiary = request.GET['beneficiary']
    ref = request.GET['ref']
    getUser = get_or_none(MtnDataShare, batchno=ref)
    smsbal = SmsangoSBulkCredit.objects.get(user=getUser)
    if status == 'Approved':
      getUser.status = 'SUCCESS'
      getUser.save()
    else:
      getUser.status = 'REFUNDED'
      smsbal.smscredit += Decimal(getUser.data_amount)
      smsbal.save()
    return HttpResponse("{'status':'DONE'}")
  except Exception as e:
    return HttpResponse("{'status': 'Parameters error'}")



def AtmDataPaystack(request):
    user = request.user
    ordernumber = request.POST.get('paystack-trxref')
    # reference = request.POST.get('reference')
    data_amt = request.POST.get('amount')
    data_number = request.POST.get('phone')
    data_network = request.POST.get('network')
    #Using ATM/BANK ==> PAYSTACK PROCEDURE SO AFTER PAYMENT ACCESS THE API TO RECHARGE USER 
    if ordernumber:
        dataapi = 'network='+data_network+'&phone='+data_number+'&amt='+data_amt
        r = requests.post(dataapi)
        info = (r.content).decode("utf-8")
        #checking the API repsonse
        if '100' in info:
            obj = MtnDataShare.objects.create(
                user = user,
                ordernumber = ordernumber,
                data_amount = int(data_amt)/100,
                data_number = data_number,
                data_network = data_network,
                status = "SUCCESS",
            )
            return render(request, 'airtime/successful_recharge_card.html')
        else:
            obj_1 = AirtimeTopup.objects.create(
                user = user,
                ordernumber = ordernumber,
                data_amount = int(data_amt)/100,
                data_number = data_number,
                data_network = data_network,
                status = "NOT SUCCESSFUL",
            )            
            return render(request, 'paystack/failure.html')
    else:
        return render(request, 'paystack/failure.html')


@login_required(login_url=settings.LOGIN_URL)
def CableCustomerCheck(request):
    template_name = "cables/customer_check_api.html"
    if request.method == "POST":
        cable_bill = request.POST.get('cable_bill')
        smart_no = request.POST.get('smart_no')
        checkcustomerapi = 'h='+cable_bill+'&smartno='+smart_no+'&jsn=json'
        checkcustomer = requests.post(checkcustomerapi)
        respon = (checkcustomer.content).decode("utf-8")
        resp = json.loads(respon)
        headling = "Decoder Information/Details Are Below <br>Result"
        return render(request, template_name, {'resp':resp, 'headling':headling})
    else:
        mssg = "Please Input Smart No"
        return render(request, template_name, {'mssg':mssg})

###TRANSACTIONS FOR ALL RECHARGE APP

@login_required(login_url=settings.LOGIN_URL)
def AirtimeTransaction(request):
    user = request.user
    template_name='airtime/airtime_transactions.html'
    transac = AirtimeTopup.objects.filter(user=user).order_by('-purchased_date')
    # paginator = Paginator(transac, 1000)#show 20 per page
    # page = request.GET.get('page')
    # try:
    #     historys = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     historys = paginator.page(1)
    # except EmptyPage:
		# # If page is out of range (e.g. 9999), deliver last page of results.
    #     historys = paginator.page(paginator.num_pages)
    return render(request, template_name, {'historys': transac, })

@login_required(login_url=settings.LOGIN_URL)
def DataTransaction(request):
    user = request.user
    template_name='datatopup/data_transactions.html'
    transac = MtnDataShare.objects.filter(user=user).order_by('-purchased_date')
    # paginator = Paginator(transac, 10)#show 20 per page
    # page = request.GET.get('page')
    # try:
    #     historys = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     historys = paginator.page(1)
    # except EmptyPage:
		# # If page is out of range (e.g. 9999), deliver last page of results.
    #     historys = paginator.page(paginator.num_pages)
    return render(request, template_name, {'historys': transac, })

@login_required(login_url=settings.LOGIN_URL)
def CableTransaction(request):
    user = request.user
    template_name='cables/cable_transaction.html'
    transac = CableRecharge.objects.filter(user=user).order_by('-purchased_date')
    return render(request, template_name, {'historys': transac, })