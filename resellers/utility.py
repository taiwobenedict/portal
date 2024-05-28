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
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView

import re, json, random, datetime, requests
from re import template

from django.contrib.auth.models import User
from resellers.models import *

from decimal import *
UserModel = get_user_model() 

def get_or_none(Model, **kwarg):
    try:
        obj = Model.objects.get(**kwarg)
        return obj
    except ObjectDoesNotExist:
        return None

"""
For processing the user order to know if the user is a Reseller or not and also determine the reseller level to assign the approriate percentage to apply
"""

# def ProcessUserReseller(user, amount, service, network):
#   try:
#     get_reseller_user = get_or_none(ResellerStatus, user=user)
#     if get_reseller_user != None:
#       get_reseller_pkg = get_or_none(ResellerLevelsAndPercentage, name=get_reseller_user.reseller_level, is_active=True)
#       if get_reseller_pkg != None:
#         get_service_json = getattr(get_reseller_pkg, service)

#         get_json_percent = json.loads(get_service_json)

#         get_percent = get_json_percent[network]

#         # print(get_percent, "percentage", amount)

#         get_reseller_amt = float(amount) - (get_percent * float(amount))

#         """ RETURN RESELLER AMOUNT TO THE AMOUNT TO BE DEDUCTED"""
#         return (get_reseller_amt, True)
#     else:
#       return ('error', False)
#   except Exception as e:
#     return ('error', False)

def ProcessUserReseller(user, amount, service, network, what_user_sees=None):
  try:
    get_reseller_user = get_or_none(ResellerStatus, user=user)
    get_reseller_amt = amount
    if get_reseller_user != None:
      get_reseller_pkg = get_or_none(ResellerLevelsAndPercentage, name=get_reseller_user.reseller_level, is_active=True)
      if get_reseller_pkg != None:
        get_service_json = getattr(get_reseller_pkg, service)

        get_json_percent = json.loads(get_service_json)

        get_data = get_json_percent[network]

        if service == "data":
          get_data = get_data.split(",")
          for item in get_data:
            if what_user_sees is not None and what_user_sees in item:
              get_reseller_amt = item.split("|")[1]
          return (get_reseller_amt, True)
        
        if service == "cable_tv":
          get_data = json.load(get_data)
          for item in get_data:
            if what_user_sees is not None and what_user_sees in item:
              get_reseller_amt = item.split("|")[3]
          return (get_reseller_amt, True)

        # print(get_percent, "percentage", amount)
        get_reseller_amt = float(amount) - (get_data * float(amount))

        """ RETURN RESELLER AMOUNT TO THE AMOUNT TO BE DEDUCTED"""
        return (get_reseller_amt, True)
    else:
      return ('error', False)
  except Exception as e:
    return ('error', False)

def IsReseller(user):
    is_reseller = get_or_none(ResellerStatus, user=user)
    if is_reseller != None:
        get_r_package = ResellerLevelsAndPercentage.objects.get(name=is_reseller.reseller_level)
        return ([is_reseller, get_r_package], True)
    else:
        return (0, False)
