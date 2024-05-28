from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.core.validators import RegexValidator
import random
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, CreateView
import re
import requests, datetime
from django.utils.crypto import get_random_string
# from datetime import 
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.loader import render_to_string
from django.views import generic
from alert_system.models import AlertSystem, UserReadAlert
from monnify_app.models import MonnifyKeys
from rechargeapp.models import RechargeAirtimeAPI, DataNetworks, CableRecharegAPI
from electricity.models import ElectricityApis
from rechargeapp.utility import get_or_none
from smsangosend.forms import *
from smsangosend.utility import *
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import PricingPerSMSPerUserToPurchase, DefaultPricePerSMSToPurchase
from payments.models import *
import decimal
from more_itertools import unique_everseen
from django.contrib import messages

from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from transactions.models import Transactions
from vbp_helper.helpers import timezoneshit
from .views import HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication

from django.contrib.auth.hashers import make_password, check_password
from smsangosend.views import random_string_generator
from external_cron.views import SMSTask
from smsangosend.tasks import send_bulk_sms_bg, SendScheduledSMS_bg

from api.serializer import (SmsHistorySerializer, TransactionSerializer)
from alert_system.models import *

from monnify.monnify import Monnify
from api.models import KycApi

import ast
from django.shortcuts import render
from django.views import View

class KYCVerificationTemplate(View):
  template_name = 'api/kyc_verification.html'

  def get(self, request, *args, **kwargs):
      # Add any logic needed for the GET request
      if not request.user.is_authenticated:
        messages.error(request, "You have to be authenticated") 
        return redirect("/customer/login")
      kyc_type = request.GET.get("kyc_type")
      context = {'message': 'Hello, this is a class-based view!'}
      if kyc_type:
        type_template = "api/kyc_verification_bvn.html" if kyc_type == "BVN" else "api/kyc_verification_nin.html"
        return render(request, type_template, context)
      return render(request, self.template_name, context)