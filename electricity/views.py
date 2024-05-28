import ast
from django.http.response import JsonResponse
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from electricity.models import *
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge, GetBonusAmtToCredit
from smsangonumcredit.models import BonusesPercentage
from rechargeapp.models import BonusAccount
from api.views import QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication
from rechargeapp.utility import get_or_none
import requests, json
from electricity.serializer import electricityApiSerializer, electricitySerializer
from decimal import Decimal
from vbp_helper.helpers import evalResponse, timezoneshit
from smsangosend.signals import sendMailToUser
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction

def getTheJsonRes(info, res_params):
  try:
    res = {}
    info = json.loads(info)
    evalRes = evalResponse(info)
    for (key, value) in evalRes.items():
      for p in json.loads(res_params):
        if key == p:
          res[key] = value
    return res
  except Exception as e:#json.decoder.JSONDecodeError:
    return info

def getApiKeyElec(req):
  apiToken = req.query_params.get('api-token')
  apiTok = req.META.get('HTTP_AUTHORIZATION')

  if req.query_params.get('api-token') != None:
    return apiToken
  elif req.META.get('HTTP_AUTHORIZATION') != None:
    return apiTok
  else:
    return None

class QueryStringBasedTokenAuthentication(TokenAuthentication):
  def authenticate(self, request):
    key = getApiKeyElec(request)
    if key != None and isinstance(key, str):
      return self.authenticate_credentials(key.strip())
    else:
      pass

class HeaderBasedTokenAuthentication(TokenAuthentication):
  def authenticate(self, request):
    if request.META.get('HTTP_AUTHORIZATION') != None:
      return self.authenticate_credentials(request.META.get('HTTP_AUTHORIZATION').strip())
    else:
      pass



def splitElectricityCode(name, array):
  print('+++>', name, array)
  try:
    code = None
    for i in array:
      codi = i.split('|')
      # cod = codi[1].lower()
      if codi[0].lower() == name.lower() or codi[1].lower() == name.lower() or codi[2].lower():
        code = i.split('|')
        print('==>', code)
    return code
  except Exception as e:
    return "error"

class electricityCustomerCheck(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      token = getApiKeyElec(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)

      getUser = get_or_none(Token, key=token)
      if getUser != None:
        user = getUser.user
        service_r = params.get('service')
        meterNo = params.get('meterNo')
        code = params.get('code')
        getCustomerCheckUrl = ElectricityApis.objects.get(is_active=True, identifier=params['code'])
        print(getCustomerCheckUrl.electricity_code_json, service_r)
        service = splitElectricityCode(service_r, json.loads(getCustomerCheckUrl.electricity_code_json))
        print(service)
        print(service_r)
        print(meterNo)
        if service != "error":
          service = service[0].strip()
          url = (getCustomerCheckUrl.api_url_check).strip()
          url = url.replace("[SERVICE]",service)
          url = url.replace("[METER_NO]",meterNo.strip())
          print(url)
          r = requests.get(url)
          info = (r.content).decode("utf-8")
          print(info)
          if 'successfully' in str(info):
            info = json.loads(info)
            return Response({'status':200, 'message':'Customer details retrieved successfully', 'details':info['details']})
          else:
            resJson = {}
            resJson['vbpMeterNo'] = meterNo
            resJson['vbpService'] = service
            return Response({'status':400, 'message':'Validation Error', 'details':resJson})
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Validation Error', 'details':'Bad Request'})
    return Response({'status':400, 'message':'Validation Error', 'details':'Bad Request'})

class electricityPurchase(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  @transaction.atomic
  def post(self, request):
    try:
      params = request.query_params
      token = getApiKeyElec(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      
      if len(params) :
        pass
      else:
        params = json.loads(request.body)

      user = getUser.user
      getCustomerCheckUrl = ElectricityApis.objects.get(is_active=True, identifier=params['code'])
      service_p = params['service']
      print(service_p)
      meterNo = params['meterNo']
      mType = params['meterType']
      mTypec = splitElectricityCode(mType, json.loads(getCustomerCheckUrl.metertype_code_json))
      print(mTypec)
      meterType = mTypec[0]
      serviceCode = params.get('serviceCode',  str('None'))
      amount= params.get('amount',  str('None'))
      phoneNumber = user.userprofile.phone
      email = user.email
      customerName = params.get('customerName',  str('None'))
      customerAddress = params.get('customerAddress',  str('None'))
      customerAccountType = params.get('customerAccountType',  str('None'))
      customerDtNumber = params.get('customerDtNumber',  str('None'))
      transactionID = params.get('transactionID',  str('ELEC'+ get_random_string(length=10)))
      uniqueCode = params.get('uniqueCode', str('None'))
      from api.models import ApiKeyActivation
      chkApiAcc = get_or_none(ApiKeyActivation, domain=request.META.get('HTTP_SOURCE_DOMAIN'))
      mode = "DIRECT" if chkApiAcc is None  else "API"

      # checkApiBalanceAgainstAmt(amount)
      service_s = splitElectricityCode(service_p, json.loads(getCustomerCheckUrl.electricity_code_json))
      print(service_s)
      if service_s != "error" and service_s != None:
        service = service_s[2].strip()
        serviceName = service_s[3].strip()
        # print(serviceName)
        # print(service)
        # print(serviceCode)
        smsbal = SmsangoSBulkCredit.objects.get(user=user)
        old_balance = smsbal.smscredit
        bonuscre = BonusAccount.objects.get(user=user)
        compare = float(int(amount)) + getCustomerCheckUrl.commission <= smsbal.smscredit

        if (float(int(amount)) + getCustomerCheckUrl.commission) > float(user.smsbulkcredit.smscredit) or int(user.smsbulkcredit.smscredit) <= 0 or (float(int(amount)) + getCustomerCheckUrl.commission) <= 0:
          # t.comment = "Insufficient CREDIT"
          # t.status = "FAILED"
          # t.save()
          return Response({'status':400, 'message':'Error', 'details':"Insufficient Balance"}, status=400)

        if compare is False:
          return Response({'status':400, 'message':'Error', 'details':"Insufficient Balance"}, status=400)

        amount = float(int(amount)) + getCustomerCheckUrl.commission
        amt = abs(float(int(amount)))

        from resellers.utility import ProcessUserReseller
        is_reseller = ProcessUserReseller(user, amt, 'electricity', service)
        if is_reseller[1] is True:
          amt = is_reseller[0]
          # print(amount)

        smsbal.smscredit -= Decimal(float(amt))
        smsbal.save()

        from transactions.models import Transactions

        Transactions.objects.create(
            user = user,
            bill_type = "ELECTRICITY",
            bill_code = f"{service}|{serviceName}|{meterType}|{serviceCode}|{customerAccountType}|{uniqueCode}",
            bill_number = meterNo,
            identifier = params['code'],
            actual_amount = amount,
            paid_amount = amt,
            old_balance = old_balance,
            new_balance = smsbal.smscredit,
            status = "QUEUE",
            api_id = getCustomerCheckUrl.id,
            mode = mode,
            reference = timezoneshit(),
            phone = phoneNumber,
            email = email,
            customernumber = customerDtNumber,
            customername = customerName,
        )

        return Response({'status':201, 'message':'Submited Successfully', 'details':'Request has been submitted successfully', 'balance': smsbal.smscredit}, status=201)
      else:
        return Response({'status':400, 'message':'Error', 'details':'Error'}, status=400)    
    except Exception as e:
      return Response({'status':400, 'message': 'Bad requests', 'details':str(e)}, status=400)
    return Response({'status':400,'message': 'Bad requests', 'details':'Bad Requests'}, status=400)

@transaction.atomic
def ProcessElectricityPurchase(object_id):
  from transactions.models import Transactions
  t = Transactions.objects.get(pk=object_id, status="QUEUE")
  # t.status = "PROCESSING"
  # t.save()
  user = t.user
  getCustomerCheckUrl = get_or_none(ElectricityApis, is_active=True, pk=t.api_id)
  # print(getCustomerCheckUrl, "ooopppoooo", object_id)
  ordernumber = t.reference
  t.reference = ordernumber
  [service, serviceName, meterType, serviceCode, customerAccountType, uniqueCode] = t.bill_code.split("|")
  amount = t.actual_amount
  if getCustomerCheckUrl is None:
    t.comment = "api not activated, contact the admin"
    t.save()
    return ""

  if int(float(amount) + float(t.new_balance)) != int(t.old_balance):
    t.comment = "Insufficient CREDIT/Fraud detected"
    t.status = "FAILED"
    t.save()
    return "Done"

  else:
    url = (getCustomerCheckUrl.api_url).strip()
    url_data = getCustomerCheckUrl.api_url_data
    replace_keys = (('[SERVICE]',service),('[METER_NO]',t.bill_number),('[SERVICE_CODE]',serviceCode),('[SERVICE_NAME]',serviceName),\
      ('[METER_TYPE]',meterType),('[PHONE_NUMBER]',t.phone),('[EMAIL]',t.email),('[CUSTOMER_NAME]',t.customername),('[CUSTOMER_ACCOUNT_TYPE]',customerAccountType),\
          ('[CUSTOMER_DT_NUMBER]', t.customer_dt_number),('[AMOUNT]',str(int(amount))),('[TRANSACTION_ID]',t.reference), ('[UNIQUE_CODE]',uniqueCode), ('[CUSTOMER_REFERENCE]', t.bill_number))
    for (i,j) in replace_keys:
      url = url.replace(i,j)
      url_data = str(url_data).replace(i,j)
    paramet = ast.literal_eval(url_data)
    # print(url)
    print(url_data)
    bonuscre = BonusAccount.objects.get(user=user)

    #Process if User is Reseller
    from resellers.utility import ProcessUserReseller
    is_reseller = ProcessUserReseller(user, amount, 'electricity', service)

    from vbp_helper import request_method
    info = request_method.call_external_api(url, paramet['data'], paramet['headers'])

    if any(respo in str(info) for respo in getCustomerCheckUrl.success_code.split(",")):

      info = json.loads(info.decode())
      jinfo = evalResponse(info)
      jinfo['site_amount'] = amount
      print(info)

      t.api_response = json.dumps(jinfo)
      t.status = "SUCCESS"
      t.save()

      if is_reseller[1] is True:
        pass
      else:
        bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
        if bonus_to_add is None:
          pass
        else:
          getbonus_amt = GetBonusAmtToCredit(bonus_to_add, 'purchase_electricity_bonus', getCustomerCheckUrl.identifier)
          bonuscre.bonus += Decimal(getbonus_amt * float(amount))
          bonuscre.save()
          getrefbonus_percent = GetBonusAmtToCredit(bonus_to_add, 'referral_electricity_bonus', getCustomerCheckUrl.identifier)
          getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
          CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)

      #subject = 'Electricity Receipt'
      #fetchInfo = json.loads(info)
      #x = evalResponse(fetchInfo)
      #message = render_to_string('electricity/electricity_email_message.html',{
      #  'user': user, 'amount':amount, 'transactionId':transactionID, #'service':service, 'customerName':customerName, #'customerAddress':customerAddress, 'meterNo':meterNo
      #})
      #sendMailToUser.send(sender=None, user=user, subject=subject, message=message)

      return Response({'status':201, 'message':'Success', 'details':"Successful"})
    else:
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      smsbal.smscredit += Decimal(float(amount))
      smsbal.save()

      t.api_response = info
      t.new_balance = smsbal.smscredit
      t.paid_amount = 0
      t.status = "FAILED"
      t.save()

      from api_errors.views import ReturnErrorResponse
      resp = ReturnErrorResponse(info, getCustomerCheckUrl.api_name, "Payment failed")

  if t.callback_url:
    request_method.call_external_api(t.callback_url, {"status": t.status}, {})    


class electricityTransactions(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = Electricity.objects.filter(user=user).order_by('-date')
      transac = electricitySerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Electricity transaction retrieve successfully', 'details': transac.data})
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'})

class electricityTransactionDetails(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      if getUser != None:
        user = getUser.user
        getElect = Electricity.objects.get(user=user, trans_id=params['transId'])

        get_res_params = get_or_none(ElectricityApis, is_active=True, identifier=getElect.identifier).res_params
        # print(getElect.api_response, '\n\n', get_res_params)
        details = getTheJsonRes(getElect.api_response, get_res_params)

        print(details, '------>><<------')

        return Response({'status':200, 'message':'Electricity transaction retrieve successfully', 'details': details})
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'})


###########Template View###########
@login_required(login_url=settings.LOGIN_URL)
def electricityPurchaseView(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')
  template_name = "general/general_layout.html"
  api_obj = ElectricityApis.objects.filter(is_active=True)
  return render(request, template_name, {'products':api_obj, 'title': "Electricity", 'link': '/customer/electricity/electricityProcessPurchase'})

@login_required(login_url=settings.LOGIN_URL)
def electricityProcessPurchaseView(request, code):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')
  obj = ElectricityApis.objects.get(is_active=True, identifier=code)
  return render(request, 'electricity/electricityPurchase.html', 
  {"array":json.loads(obj.electricity_code_json), "metertypearr":json.loads(obj.metertype_code_json), "obj": obj})

def electricityTransactionsPage(request):
    user = request.user
    template_name='electricity/electricityHistory.html'
    transac = Electricity.objects.filter(user=user).order_by('-date')
    return render(request, template_name, {'historys': transac})

@api_view(['GET'])
def listElectricityServices(request):
  list_of_elec = ElectricityApis.objects.filter(is_active=True)
  serializer = electricityApiSerializer(list_of_elec, many=True)
  new_data = {"status": 200, "result": serializer.data}
  return Response(new_data, status=200)