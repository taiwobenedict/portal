import ast
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
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
from electricity.models import *
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge,GetBonusAmtToCredit
from smsangonumcredit.models import BonusesPercentage
from rechargeapp.models import BonusAccount
from api.views import QueryStringBasedTokenAuthentication
from rechargeapp.utility import get_or_none
import requests
import json
from decimal import Decimal
from education.models import *
from education.serializer import ResultCheckersSerializer 
from vbp_helper.helpers import evalResponse
from django.conf import settings
from django.db import transaction

def getTheJsonRes(info, res_params):
  try:
    res = {}
    info = info if isinstance(info, dict) else json.loads(info)
    evalRes = evalResponse(info)
    for (key, value) in evalRes.items():
      for p in json.loads(res_params):
        if key == p:
          res[key] = value
    return res
  except json.decoder.JSONDecodeError:
    # print('empty')
    return info

def getApiKey(req):
  apiToken = req.query_params.get('api-token')
  apiTok = req.META.get('HTTP_AUTHORIZATION')

  if req.query_params.get('api-token') != None:
    return apiToken
  elif req.META.get('HTTP_AUTHORIZATION') != None:
    return apiTok
  else:
    return None

def splitResultCheckerCode(name, array):
  print('+++>', name, array)
  try:
    code = None
    for i in array:
      codi = i.split('|')
      # cod = codi[1].lower()
      if codi[0].lower() == name.lower() or codi[1].lower() == name.lower():
        code = i.split('|')
        print('==>', code)
    return code
  except Exception as e:
    return "error"

@transaction.atomic
def RouteToThePin(pin_type, user):
  try:
    ["pin_type|api_price|site_price|product_code|urlvariable"]
    getActiveApi = ResultCheckerAPIs.objects.get(is_active=True, identifier=pin_type)

    service = splitResultCheckerCode(pin_type, json.loads(getActiveApi.pin_code_json))
    pin_type, api_price, amount, product_code, urlvariable = service[0], service[1], service[2], service[3], service[4]
    ordernumber = str(pin_type[0]+pin_type[1]+pin_type[2]+ get_random_string(length=10))
    smsbal = SmsangoSBulkCredit.objects.get(user=user)
    old_balance = smsbal.smscredit
    bonuscre = BonusAccount.objects.get(user=user)
    compare = float(int(amount)) <= smsbal.smscredit
    if compare is True:
      url = (getActiveApi.api_api_url).strip()
      url_data = (getActiveApi.api_url_data).strip()
      replace_keys = (('[SERVICE]',pin_type),('[TRANSACTION_ID]',ordernumber),('[PRICE]',api_price),('[PRODUCT_CODE]',product_code),\
        ('[URL_VARIABLE]',urlvariable), ('[PHONE]',user.userprofile.phone), ('[AMOUNT]',amount))
      for (i,j) in replace_keys:
        url = url.replace(i,j)
        url_data = str(url_data).replace(i,j)
      paramet = ast.literal_eval(url_data)
      print(url)
      print(url_data)

      #Process if User is Reseller
      from resellers.utility import ProcessUserReseller
      is_reseller = ProcessUserReseller(user, amount, 'education', pin_type)
      if is_reseller[1] is True:
        amount = is_reseller[0]

      smsbal.smscredit -= Decimal(amount)
      smsbal.save()
      result_obj = ResultCheckers.objects.create(
        user = user,
        trans_id = ordernumber,
        amount = float(amount),
        pin = "",#json.dumps(jinfo),
        serial_number = "", #json.dumps(jinfo),
        pin_type = pin_type,
        identifier = pin_type,
        old_balance = float(old_balance),
        new_balance = float(smsbal.smscredit),
        status = "SUCCESS",
      )

      from vbp_helper import request_method
      info = request_method.call_external_api(url, paramet['data'], paramet['headers'])
      print(info)

      if any(respo in str(info) for respo in getActiveApi.success_code.split(",")):

        jinfo = ''
        if isinstance(info, dict):
          jinfo = info
        else:
          info = json.loads(info)
          jinfo = evalResponse(info)

        jinfo['site_amount'] = amount

        result_obj.pin = json.dumps(jinfo)
        result_obj.serial_number = json.dumps(jinfo)
        result_obj.status = "SUCCESS"
        result_obj.save()

        if is_reseller[1] is True:
          pass
        else:
          bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
          if bonus_to_add is None:
            pass
          else:
            try:
              getbonus_amt = GetBonusAmtToCredit(bonus_to_add,'education_bonus', getActiveApi.identifier)
              bonuscre.bonus += Decimal(getbonus_amt * float(amount))
              bonuscre.save()
              getrefbonus_percent = GetBonusAmtToCredit(bonus_to_add,'referral_education_bonus', getActiveApi.identifier)
              getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
              CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
            except:
              pass
        return info
      else:
        smsbal.smscredit += Decimal(amount)
        smsbal.save()

        result_obj.pin = json.dumps(info)
        result_obj.serial_number = json.dumps(info)
        result_obj.new_balance = smsbal.smscredit
        result_obj.status = "FAILED"
        result_obj.save()

        from api_errors.views import ReturnErrorResponse
        resp = ReturnErrorResponse(info, getActiveApi.api_name, "notsuccessful")
        return 'notsuccessful'
    return "insufficient balance"
  except Exception as e:
    # raise e
    return 'error'

class ResultCheckerView(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  @transaction.atomic
  def post(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      if getUser != None:
        user = getUser.user
        pin_type = params['pin_type']
        info = RouteToThePin(pin_type, user)
        if info == "insufficient balance":
          return Response({'status':400, 'message':'Insufficient Balance'})
        elif info == "error":
          return Response({'status':400, 'message':'Error contact the site admin'})
        elif info == 'notsuccessful':
          return Response({'status':400, 'message':'Purchase not successful or service not available consult the admininstrator'})
        else:
          ressJson = {}
          info = info if isinstance(info, dict) else json.loads(info)
          details = evalResponse(info)             
          return Response({'status':201, 'message':'Pin Purchased successfully', 'details':details})
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Validation Error', 'details':'Bad Request'})
    return Response({'status':400, 'message':'Validation Error', 'details':'Bad Request'})

class educationTransactions(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      transac = ResultCheckers.objects.filter(user=user).order_by('-date')
      transac = ResultCheckersSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Education transaction retrieve successfully', 'details': transac.data})
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'})

@login_required(login_url=settings.LOGIN_URL)
def PinTransaction(request):
    user = request.user
    template_name='education/pinHistory.html'
    transac = ResultCheckers.objects.filter(user=user).order_by('-date')
    paginator = Paginator(transac, 10)#show 20 per page
    page = request.GET.get('page')
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        historys = paginator.page(1)
    except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
        historys = paginator.page(paginator.num_pages)
    return render(request, template_name, {'historys': transac, })

###########Template View###########
@login_required(login_url=settings.LOGIN_URL)
def PinPurchaseView(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')
  template_name = "general/general_layout.html"
  api_obj = ResultCheckerAPIs.objects.filter(is_active=True)
  return render(request, template_name, {'products':api_obj, 'title': "Education", 'link': '/customer/education/educationProcessPurchase'})

@login_required(login_url=settings.LOGIN_URL)
def PinProcessVeiw(request, code):
  template_name = "education/pinPurchase.html"
  obj = ResultCheckerAPIs.objects.filter(is_active=True, identifier=code)
  if len(obj) > 0:
    return render(request, template_name, {'code': code , 'obj': obj[0]})
  messages.error(request, "Something is WRONG, contact the admin for resolution")
  return render(request, template_name, {})

class GetPinDetails(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      if getUser != None:
        user = getUser.user

        transId = params['transId']

        getDetails = ResultCheckers.objects.get(user=user, trans_id=transId)

        getId = getDetails.identifier
        res_params = ResultCheckerAPIs.objects.get(is_active=True, identifier=getId).res_params

        gdetails = getDetails.pin
        details = getTheJsonRes(gdetails, res_params)

        #check if waec or neco and the only allowed field in the detailed response

        return Response({"status":200, "message":"Details retrieved successfully", "details": details})
      else:
        return Response({"status":403, "message": "Error", "details":"Not Authorized"})
    except Exception as e:
      # raise e
      return Response({"status":403, "message": "Error", "details":"Bad Request"})