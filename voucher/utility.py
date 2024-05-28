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
from rechargeapp.models import RechargeAirtimeAPI,AirtimeTopup,CableRecharge,DataPlansPrices,BonusAccount,MtnDataShare
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.views import *
from voucher.models import GeneratedVoucher

from decimal import *
UserModel = get_user_model() 

def get_or_none(Model, **kwarg):
    try:
        obj = Model.objects.get(**kwarg)
        return obj
    except ObjectDoesNotExist:
        return None

