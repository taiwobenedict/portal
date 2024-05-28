from django.shortcuts import render, redirect
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge
from smsangonumcredit.models import BonusesPercentage
from rechargeapp.models import *
from api.views import QueryStringBasedTokenAuthentication, getApiKey
from rechargeapp.utility import get_or_none
import requests, json
from decimal import Decimal
from other_data_services.models import *
from other_data_services.serializer import SmileTransactionSerializer 
from vbp_helper.helpers import evalResponse

from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


def splitCode(name, array):
  #print('+++>', name, array)
  try:
    code = None
    for i in array:
      codi = i.split('|')

      cod0 = codi[0].lower().replace('+', ' ')
      cod1 = codi[1].lower().replace('+', ' ')

      if cod0 == name.lower() or cod1.lower() == name.lower():
        print(cod1.strip()==name.lower())

        code = i.split('|')
        print('==>', code)
    return code
  except Exception as e:
    return "error"


def generateDetailsFromBroadBand(Model, user, transId, res_params):
    try:
      getTrans = get_or_none(Model, user=user, trans_id=transId)
      if getTrans != None:
        getTransac = json.loads(getTrans.resp)
        getTrans = evalResponse(getTransac)
        res = {}
        for (key, value) in getTrans.items():
          for p in json.loads(res_params):
            if key == p:
              res[key] = value
        return (res, True)
      else:
        return ('error', False)
    except Exception as e:
        # raise e
        return ('error', False)
