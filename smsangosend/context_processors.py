from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.validators import RegexValidator
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
import re
import requests
from django.views import View
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
User = get_user_model() 

from .forms import *
from smsangonumcredit.models import *
from .models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from django.core.exceptions import ObjectDoesNotExist

def Getlist_of_SMSPlan_Created(request):
    try:
        smsamttopurchase = DefaultPricePerSMSToPurchase.objects.filter(is_active=True)
        return {'request':request, 'smsamttopurchase':smsamttopurchase}
    except ObjectDoesNotExist:
        smsamttopurchase = None
        return {'request':request, 'smsamttopurchase':smsamttopurchase}
