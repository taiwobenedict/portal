import requests
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

import datetime, random, re, json
from re import template

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from payments.models import *
from rechargeapp.models import DataNetworks, RechargeAirtimeAPI, AirtimeTopup,\
  CableRecharge, BonusAccount, MtnDataShare
from rechargeapp.utility import get_or_none
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.views import *
from smsangonumcredit.models import BonusesPercentage
from decimal import *
from callbacks.models import *

UserModel = get_user_model() 

@csrf_exempt
def TransactionCallback(request, transactionId):
  from transactions.models import Transactions

  get_trans = get_or_none(Transactions, reference=transactionId, callback_done=False)
  if get_trans is None:
    return HttpResponse("Processed Before")

  if get_trans != None:
    user = get_trans.user
    get_active_callbk = None
    if get_trans.bill_type == "AIRTIME":
      get_active_callbk = get_or_none(CallbackRechargeAirtimeAPI, is_active=True)
    elif get_trans.bill_type == "DATA":      
      get_active_callbk = get_or_none(CallbackDataNetworksApi, is_active=True)
    elif get_trans.bill_type == "CABLE":
      get_active_callbk = get_or_none(CallbackRechargeAirtimeAPI, is_active=True)
    elif get_trans.bill_type == "ELECTRICITY":
      get_active_callbk = get_or_none(CallbackElectricityAPI, is_active=True)

    if get_active_callbk != None:
      if any(respo in str(request.body) for respo in get_active_callbk.callback_success_code.split(",")):
        get_trans.status = 'SUCCESS'
        get_trans.callback_done = True
        get_trans.save()
      else:
        bonuscre = BonusAccount.objects.get(user=user)
        smsbal = SmsangoSBulkCredit.objects.get(user=user)
        smsbal.smscredit += Decimal(float(get_trans.recharge_amount))
        bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
        get_trans.status = 'FAILED'
        get_trans.callback_done = True
        get_trans.save()
        try:
          if bonus_to_add is None:
            pass
          else:
            getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.purchase_airtime_bonus) 
            bonuscre.bonus -= Decimal(getbonus_amt * float(get_trans.recharge_amount))
            bonuscre.save()
            getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_airtime_bonus)
            getrefbonus_amt = -(Decimal(getrefbonus_percent * float(get_trans.recharge_amount)))
            CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
        except:
          pass
        return HttpResponse('Transaction Not Successful')
      return HttpResponse('Transaction Successful')
    return HttpResponse('Callback not activated')
  return HttpResponse('Transaction not a valid one')


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
