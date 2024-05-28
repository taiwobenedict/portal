import requests
from django.contrib import messages
from django.conf import settings

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
from django.shortcuts import get_object_or_404, redirect, render
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
from rechargeapp.models import AirtimeTopup,CableRecharge,DataPlansPrices,BonusAccount,MtnDataShare
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import *
from smsangonumcredit.views import *
from decimal import *
UserModel = get_user_model() 

def GetallDataTransaction(request):
  template_name = 'admin/sme_transactions.html'
  getAllDataTransaction = MtnDataShare.objects.all().order_by('-purchased_date')
  paginator = Paginator(getAllDataTransaction, 20)
  page = request.GET.get('page')
  try:
      historys = paginator.page(page)
  except PageNotAnInteger:
      historys = paginator.page(1)
  except EmptyPage:
      historys = paginator.page(paginator.num_pages)
  return render(request, template_name, {'historys': historys, })

@login_required(login_url=settings.LOGIN_URL)
def mtnShareWalletFunding(request):
  user = request.user
  template_name = 'payments/mtnShareFunding.html'
  if request.method == 'POST':
    phone = request.POST['phone']
    amount = request.POST['amount']
    get_user = SmsangoSBulkCredit.objects.get(user=user)
    PayStackPayment.objects.create(
      user = user,
      smsangosbulkcredit = get_user,
      order_id = 'share'+ phone,
      reference = 'share'+ phone,
      amtcredited = amount,
      amount = amount,
    )
    messages.success(request, 'Submitted Successfully')
    return redirect('smsangosend:mtnsharensell')
  return render(request, template_name, {})


