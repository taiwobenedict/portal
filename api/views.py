import ast
from api.serializer import CableApiSerializer, UserSerializer, RechargeAirtimeAPISerializer, DataNetworksSerializer
from vbp_helper import prevent_double
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
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView

import datetime
import random
import re, json
from re import template

import json
from django.contrib.auth.models import User
from payments.models import *
from rechargeapp.models import (DataNetworks,RechargeAirtimeAPI,AirtimeTopup,CableRecharge,
DataPlansPrices,BonusAccount,MtnDataShare,CableRecharegAPI)
from rechargeapp.utility import get_or_none
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.views import *
from smsangosend.forms import *
from coreconfig.models import *
from django.utils.encoding import force_bytes, force_text, smart_text 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from smsangosend.tokens import account_activation_token
from notificationapp.models import *

from decimal import *
from api.models import ApiKeyActivation
UserModel = get_user_model() 
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge, GetBonusAmtToCredit
from smsangonumcredit.models import BonusesPercentage
from django.contrib.auth.hashers import make_password, check_password
from vbp_helper.helpers import evalResponse, timezoneshit
from django.db import transaction


def SendSmsNotifications(message, sender, recipient):
  sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
  snd=[]
  for i in sendwithnotdnd:
    snd.append(i.apurl)
    snd.append(i.apiamtpersms)
    snd.append(i.api_response)
  # print(snd)
  iurl = snd[0]
  url1 = iurl.replace("[TO]", recipient.strip())
  urlt = url1.replace ("[SENDER]", sender.strip())
  apiurl = urlt.replace ("[MESSAGE]", message.strip())
  print(apiurl)
  r = requests.post(apiurl)
  info = (r.content).decode("utf-8") 
  if not snd[2] in info:
    pass
  else:
    obj = SmsangoSendSMS.objects.create(
      user = 1,
      sender = sender,
      recipients = recipient,
      messagecontent = message,
      notsently = '', #list of not sent numbers 
      sently = '', #list of sent numbers
      apiRoute = '',
      status = 'success',
      creditusedall = ''
    )
    return ''


class Test(APIView):
  def get(self, request):
    print(request.META.get('REMOTE_ADDR'), request.META.get('HTTP_X_FORWARDED_FOR'))
    return Response({"details": "hello"})
    
class apiSignup(APIView):
  def post(self, request):
    try:
      params = request.query_params
      if len(params):
        pass
      else:
        params = json.loads(request.body)
      refferal = params.get('refferal')
      phone = params.get('phone')
      username = params.get('username')
      password = params.get('password')
      email = params.get('email')
      if len(username) < 6:
        return Response({'status': 400, 'message': 'Minimum characters for username is 6'}, status=400)
      if len(password) < 6:
        return Response({'status': 400, 'message': 'Minimum characters for password is 6'}, status=400)
      if len(phone) < 11 or len(phone) > 13 or not isinstance(phone, str):
        print(isinstance(phone, int), phone, "sdfds")
        return Response({'status': 400, 'message': 'Invalid Phone Number'}, status=400)
      checkPhone = get_or_none(UserProfile, phone=phone)
      if checkPhone is not None:
        return Response({'status': 400, 'message': 'A user with that Phone Number already exist'}, status=400)
      elif UserModel.objects.filter(email = email.lower()).exists():
        return Response({'status': 400, 'message': 'Email Already exists'}, status=400)
      elif UserModel.objects.filter(username = username.lower()).exists():
        return Response({'status': 400, 'message': 'Username Already exists'}, status=400)
      else:
        user, created = User.objects.get_or_create(
          username = username.lower().strip(),
          password = make_password(password.strip()),
          defaults = {'email':email.lower().strip()}
        )
        if created == True:
          user.userprofile.refferal = 'admin' if refferal == 'undefined' else refferal
          user.userprofile.phone = phone
          user.userprofile.save()
          current_site = get_current_site(request)
          config = DashboardConfig.objects.all()            
          if len(config) == 0:
            pass
          else:
            if config[0].require_activation == True:
              subject = 'Activate Your' + config[0].site_name + 'Account'
              message = render_to_string('account_activation_email.html',{
                'user': user,'domain': current_site.domain,'uid': urlsafe_base64_encode(force_bytes(user.pk)),'token': account_activation_token.make_token(user),
              })
              user.email_user(subject, message)
              return Response({'status': 201, 'message': 'Activation Sent to your mail,\n Open the link in a browser'}, status=201)
            else:
              return Response({'status': 201, 'message':'Account created successfully'}, status=201)

        return Response({'status': 201, 'message': 'Activation Sent to your mail,\n Open the link in a browser'}, status=201)
    except Exception as e:
      raise e
      return Response({'status': 400, 'message': 'Bad Request Check Your Inputs'}, status=400)

class apiLogin(APIView):
  def post(self, request):
    try:
      params = request.query_params
      params['username']
    except:
      params = json.loads(request.body)

    print(request.body, len(request.query_params))
    username = params['username']
    password = params['password']
    try:
      user = None
      user = get_or_none(User, username=username.lower().strip())
      if not user:
        user = get_or_none(User, email=username.lower().strip())
      print(user)
      if not user.is_active:
        return Response({"message": "you are yet activate your mail"}, status=400)
      if user:
        chkpassword = check_password(password.strip(), user.password)
        print(chkpassword)
        if chkpassword:
          token, created = Token.objects.get_or_create(user=user)
          wallet = SmsangoSBulkCredit.objects.get(user=user)
          serializer = UserSerializer(user, many=False)
          new_data = serializer.data
          new_data["token"] = token.key
          new_data["message"] = 'Login Successful'
          new_data["balance"] = float(wallet.smscredit),
          new_data["status"] = 200,
          print(new_data)
          return Response(new_data, status=200)
    except Exception as e:
      raise e
      return Response({'status': 400, 'message': 'Bad Credentials'}, status=400)
    return Response({'status': 400, 'message': 'Bad Credentials'}, status=400)

class apiPasswordReset(APIView):
  def post(self, request):
    params = request.query_params
    email = params['email']
    phone = params['phone']
    password = params['password']
    try:
      user = get_or_none(User, email=email.strip())
      if user:
        createPassword = make_password(password.strip())
        user.password = createPassword
        user.save()
        return Response({'status': 200, 'message': 'Password Change Successful'}, status=200)
    except Exception as e:
      return Response({'status': 400, 'message': 'Bad Credentials'}, status=400)
    return Response({'status': 400, 'message': 'Bad Credentials'}, status=400)


# from ipware import get_client_ip
def getApiKey(req):
  # client_ip, is_routable = get_client_ip(req)

  # chk_ip = UserProfile.objects.filter(ip=client_ip)
  # if chk_ip.exists():

  get_domain = req.META.get("HTTP_SOURCE_DOMAIN")
  print(get_domain, "get_domain")
  if get_domain != None:
    try:
      chkApiAcc = ApiKeyActivation.objects.filter(domain=get_domain)
      if not chkApiAcc or not chkApiAcc[0].api_user or not chkApiAcc[0].verified:
        return None
      else:
        pass
    except Exception as e:
      raise e
      return None
  # else:
  #   return None

  apiToken = req.query_params.get('api-token')
  apiTok = req.META.get('HTTP_AUTHORIZATION')

  if req.query_params.get('api-token') != None:
    return apiToken
  elif req.META.get('HTTP_AUTHORIZATION') != None:
    return apiTok
  else:
    return None
  # else:
  #   return None


class QueryStringBasedTokenAuthentication(TokenAuthentication):
  def authenticate(self, request):
    key = getApiKey(request)
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

	  
class apiProfileUpdate(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def put(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      params = request.query_params
      if len(params):
        pass
      else:
        params = json.loads(request.body)
      firstname = params.get('first_name')
      lastname = params.get('last_name')
      location = params.get('location')
      dob = params.get('dob')
      if getUser:
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        user.userprofile.location = location
        user.userprofile.date_of_birth = dob
        user.userprofile.save()
        token, created = Token.objects.get_or_create(user=user)
        wallet = SmsangoSBulkCredit.objects.get(user=user)
        serializer = UserSerializer(user, many=False)
        new_data = serializer.data
        print(new_data, "shdhs")
        new_data["token"] = token.key
        new_data["message"] = 'Update Successful'
        new_data["balance"] = float(wallet.smscredit),
        new_data["status"] = 200,
        print(new_data)
        return Response(new_data, status=200)
    except Exception as e:
      return Response({'status': 400, 'message': 'update not successful'}, status=400)
    return Response({'status': 400, 'message': 'update not successful'}, status=400)

@login_required(login_url=settings.LOGIN_URL)
def CreateApiToken(request):
  template_name = 'api/generate-api.html'
  try:
    user = request.user
    toPayForKey = DashboardConfig.objects.all()[0]
    if toPayForKey.allow_payment_for_apikey == True:
      check_if_paid = get_or_none(ApiKeyActivation, user=user)
      if check_if_paid == None:
        context = {
          'message':'You need to pay to access token'
        }
        return render(request, template_name, context)
      else:
        token, created = Token.objects.get_or_create(user=user)
        domain, created = ApiKeyActivation.objects.get_or_create(user=request.user)
        print(token)
        context = {
          'token':token.key,
          'domain': domain,
          "dconfig": toPayForKey 
        }
        return render(request, template_name, context)
    else:
      token, created = Token.objects.get_or_create(user=user)
      domain, created = ApiKeyActivation.objects.get_or_create(user=request.user)
      print(token)
      context = {
        'token':token.key,
        'domain': domain,
        "dconfig": toPayForKey 
      }
      return render(request, template_name, context)
  except Exception as e:
    context = {
      'message': 'Bad Request Your Parameters'
    }
    return render(request, template_name, context)
  return render(request, template_name)

@login_required(login_url=settings.LOGIN_URL)
def UpdateDomain(request):
  template_name = 'api/generate-api.html'
  if request.method == "POST":
    domain = request.POST.get("domain")
    print(domain, "hello domain")

    if domain is None or "localhost" in domain or "127.0.0.1" in domain or "https" not in domain:
      messages.error(request, "domain is required")
      return redirect("api:generate_token")
    else:
      user_p, created = ApiKeyActivation.objects.get_or_create(user=request.user)
      user_p.domain = domain
      user_p.api_user = True
      user_p.save()
      messages.success(request, "Domain added")
      return redirect("api:generate_token")
  return redirect("api:generate_token")

@login_required(login_url=settings.LOGIN_URL)
def verifyDomain(request):
  user = request.user
  getApiPro = ApiKeyActivation.objects.filter(user=user)
  if getApiPro.exists():
    getApiPro = getApiPro.last()
    config = DashboardConfig.objects.all()[0]
    print(config.api_text, "api_text")

    from vbp_helper import request_method
    info = request_method.call_external_api(getApiPro.domain + "/vbp.txt", {}, {})
    print(info)

    if any(respo in str(info) for respo in config.api_text.split(",")):
      getApiPro.verified = True
      getApiPro.save()

      messages.success(request, "Domain verified")
      return redirect("api:generate_token") 
    messages.error(request, "Error verifiying domain")
    return redirect("api:generate_token") 
  return redirect("api:generate_token")


class HelloView(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)

  def get(self, request):
    try:
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      print(getUser.user.username)
      if getUser:
        content = {'message': 'Hello, World!'}
        return Response(content)
    except Exception as e:
      return Response({'status': 400, 'message': 'Bad Request Your Parameters'}, status=400)

####API GET USER DASHBOARD PROFILE
class apiGetUserDetails(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      if user:
        balance = get_or_none(SmsangoSBulkCredit, user=user)
        getallreffered = UserProfile.objects.filter(refferal=user.username)
        bonus = get_or_none(BonusAccount,user=user)
        getNotReadNote = ReadNotification.objects.filter(user=user)
        getNote= Notification.objects.filter(~Q(readonly__in=getNotReadNote)).order_by('-createdAt')[:3]
        content = {
          'status':200, 
          'message':'success',
          'balance':balance.smscredit,
          'refcount': len(getallreffered),
          'bonus': bonus.bonus,
          'username': user.username,
          'phone': user.userprofile.phone,
          'getNote': len(getNote)
          }
        return Response(content,status=HTTP_200_OK)
    except Exception as e:
      return Response({'status': 400, 'message': 'Bad Request Check Your Parameters'}, status=400)

class apiGetUserProfile(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      if user:
        content = {
          'status':200, 
          'message':'success',
          'details': {
            'firstname': user.first_name,
            'lastname': user.last_name,
            'phone': user.userprofile.phone,
            'location': user.userprofile.location,
            'dob': user.userprofile.date_of_birth,
            }
          }
        return Response(content,status=HTTP_200_OK)
    except Exception as e:
      return Response({'status': 400, 'message': 'Bad Request Check Your Parameters'}, status=400)


####API BALANCE
class ApiBalance(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      if user:
        balance = get_or_none(SmsangoSBulkCredit, user=user)
        content = {'status':200, 'message':'success', 'balance':balance.smscredit }
        return Response(content,status=HTTP_200_OK)
    except Exception as e:
      return Response({'status': 400, 'message': 'Bad Request Check Your Parameters'}, status=400)

####API AIRTIME 
class ApiAirtimeView(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)

  def get(self, request):
    objs = RechargeAirtimeAPI.objects.filter(is_active=True)
    serializer = RechargeAirtimeAPISerializer(objs, many=True)
    # print(serializer.data)
    # serializer.data["status"] = 200
    new_data = {"status": 200, "result":serializer.data}
    return Response(new_data, status=200)

  @transaction.atomic
  def post(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user

      if not user.userprofile.phone:
        return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)
      if len(params):
        pass
      else:
        params = json.loads(request.body)
      network = params['network']
      phone = params['phone']
      amt = params['amount']
      amt = abs(int(amt))
      if amt <= 0:
        return Response({'message': 'Amount cant be zero or less'}, status=400)
      callback_url = params.get('callback_url')
      if prevent_double.prevent_doubles(request, network, phone):
        return ({'status':400, 'message':'Too Immediate', 'details':'Transaction error this seems to be a duplicate request else retry in a minute'})
      # checkApiBalanceAgainstAmt(amt)
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      old_balance = smsbal.smscredit
      bonuscre = BonusAccount.objects.get(user=user)
      #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
      compare = float(int(amt)) <= smsbal.smscredit
      act_amt = float(int(amt))
      
      if float(amt) > float(user.smsbulkcredit.smscredit):
        return Response({'status':400, 'message':'Error', 'details': 'Insufficient Balance'}, status=400)
      else:
        api_obj = get_or_none(RechargeAirtimeAPI, is_active=True, identifier=network)
        if api_obj == None:
          return Response({'status':400, 'message':'Error', 'details': 'Contact the Administrator'}, status=400)

        smsbal = user.smsbulkcredit
        old_balance = smsbal.smscredit

        from resellers.utility import ProcessUserReseller
        is_reseller = ProcessUserReseller(user, float(amt), 'airtime', api_obj.identifier)

        if is_reseller[1] is True:
          amt = is_reseller[0]

        smsbal.smscredit -= Decimal(float(amt))
        smsbal.save()

      from transactions.models import Transactions

      Transactions.objects.create(
        user = user,
        bill_type = "AIRTIME",
        bill_code = network,
        bill_number = phone,
        identifier = network,
        actual_amount = act_amt,
        old_balance = old_balance,
        new_balance = smsbal.smscredit,
        paid_amount = amt,
        status = "QUEUE",
        api_id = api_obj.id,
        reference = timezoneshit(),
        mode = "API",
        callback_url = callback_url
      )
      return Response({'status':201, 'message':'success', 'details': 'Transaction Submitted', 'balance': smsbal.smscredit}, status=201)
    except Exception as e:
      raise e
      return Response({'status': 400, 'message':'error', 'details': 'one or more fields are missing please check'}, status=400)

##### AIRTIME END

####### DATA API 
def GetPrice(data_network, data_size):
  try:
    print('dataNETWORK>>>>', data_network, data_size)
    get_active_api = get_or_none(DataNetworks, is_active=True, identifier=data_network)
    dataNet = get_active_api.network_data_amount_json.split(',')
    print('dataNet>>>>', dataNet)
    # dataSizeSplit = data_size.split("|")
    getOtherParam, getplancd = {}, {}
    for x in dataNet:
      if data_size.lower() == x.split('|')[2].lower() or data_size.lower() == x.split('|')[3].lower():
        print(x, "..................////")
        getplancd['otplan_code'] = x
    getOtherParam = getplancd['otplan_code'].split('|')
    print(getOtherParam)
    return getOtherParam
  except Exception as e:
    raise e
    return 'error'

class ApiDataView(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)


  def get(self, request):
    if request.GET.get("identifier"):
      obj = DataNetworks.objects.get(identifier=request.GET.get("identifier"));
      plans = obj.network_data_amount_json
      return Response({"status": 200, "result": plans}, status=200)

    objs = DataNetworks.objects.filter(is_active=True)
    serializer = DataNetworksSerializer(objs, many=True)
    new_data = {"status": 200, "result":serializer.data}
    return Response(new_data, status=200)


  @transaction.atomic
  def post(self, request):

    try:
      params = request.query_params
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      if not user:
        return Response({"details": "Cannot be authenticated"},  status=403)
      if not user.userprofile.phone:
        return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)

      if len(params):
        pass
      else:
        params = json.loads(request.body)
      data_network = params['network']
      data_number = params['phone']
      data_size = params['amount']
      callback_url = params.get('callback_url')
      if prevent_double.prevent_doubles(request, data_network, data_number):
        return ({'status':400, 'message':'Too Immediate', 'details':'Transaction error this seems to be a duplicate request else retry in a minute'})
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      bonuscre = BonusAccount.objects.get(user=user)
      #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
      getOtherParam = GetPrice(data_network, data_size)
      apiamount, data_amount, apicode, urlvariable = getOtherParam[0],\
        getOtherParam[1], getOtherParam[2], getOtherParam[3]
      getOtherParam = '|'.join(getOtherParam)
      compare = float(data_amount) <= smsbal.smscredit
      old_balance = smsbal.smscredit
      # checkApiBalanceAgainstAmt(data_amount)
      act_data_amount = data_amount
      if compare is not True:
        return Response({'status':200, 'message':'Error', 'details': 'Insufficient Balance'}, status=200)
      dataapi = get_or_none(DataNetworks, is_active=True, identifier=data_network)
      if dataapi == None:
        return Response({'status':500, 'message':'contact the adminstrator'}, status=500)


      from resellers.utility import ProcessUserReseller
      is_reseller = ProcessUserReseller(user, float(data_amount), 'data', dataapi.identifier, apicode)

      if is_reseller[1] is True:
        data_amount = is_reseller[0]

      smsbal.smscredit -= Decimal(float(data_amount))
      smsbal.save()

      from transactions.models import Transactions


      Transactions.objects.create(
          user = user,
          bill_type = "DATA",
          bill_code = getOtherParam,#data_size.strip(),
          bill_number = data_number,
          identifier = data_network,
          actual_amount = act_data_amount,
          old_balance = old_balance,
          new_balance = smsbal.smscredit,
          paid_amount = data_amount,
          status = "QUEUE",
          api_id = dataapi.id,
          mode = "API",
          reference = timezoneshit(),
          callback_url = callback_url
      )
      return Response({'status':201, 'message':'success', 'details': 'Transaction Submitted', 'balance': smsbal.smscredit}, status=201)
    except Exception as e:
      raise e
      return Response({'status': 400, 'message':'error', 'details': 'Bad Request Check Your Parameters'}, status=400)

#### DATA END


#####CABLE API
def splitStuffs(string, splitwith):
  splitted = string.split(splitwith)
  return splitted

def listCableTv(request):
  tv = request.GET['service']
  getActiveApi = get_or_none(CableRecharegAPI, is_active=True)
  if getActiveApi != None:
    service_code = splitStuffs(getActiveApi.cable_amount_json, '/')
    service = []
    for i in service_code:
      print(i)
      if tv.upper() in i or tv.lower() in i:
        x = i.split("=")
        print(x)
        for a in x[1].split(","):
          item = {}
          s_a = a.split("|")
          item['api_amount'] = s_a[0].split(":")[1]
          item['site_amount'] = s_a[1]
          item['api_plan_code'] = s_a[2]
          item['api_service_code'] = s_a[3]

          service.append(item)      

    return JsonResponse({"status":200, "message":"plans retreived", "details":service})
  return JsonResponse({"status":400, "message":"error"})

def listCableTvs(request):
  objs = CableRecharegAPI.objects.filter(is_active=True)
  serializer = CableApiSerializer(objs, many=True)
  return JsonResponse({"status":200, "result": serializer.data}, status=200)


class ApiCheckCustomer(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user

      # if not user.userprofile.phone:
      #   return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)
      smart_no, service  = params['smart_no'], params['service']
      getActiveApi = get_or_none(CableRecharegAPI, is_active=True, identifier=service)
      if getActiveApi == None:
        return Response({'status': 400, 'message':'error', 'details':'No API Activated, Contact The Admin'}, status=400)
      service_code = json.loads(getActiveApi.cable_type_price)
      eurl = getActiveApi.customerCheck
      url = eurl.replace('[SMART_NO]', smart_no)
      url = url.replace('[SERVICE]', service)
      r = requests.get(url)
      get_resp = r.content.decode("utf-8")
      get_resp = json.loads(get_resp)
      get_resp['status'] = 200
      get_resp['message'] = 'success' 
      return Response(get_resp, status=200)
    except Exception as e:
      raise e
      return Response({'status': 400, 'message':'error', 'details': 'Bad Request Your Parameters'}, status=400)


class ApiCableRecharge(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication, QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  @transaction.atomic
  def post(self, request):

    try:
      params = request.query_params
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      if not user:
        return Response({"details": "Cannot be authenticated"},  status=403)
      if not user.userprofile.phone:
        return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)

      if len(params):
        pass
      else:
        params = json.loads(request.body)

      """ Only the smart_no, service, otplancode, customer_name are important """
      service, phone, smart_no, customer_name, customer_number, otplacn_code, invoice =\
        params.get('service'), params.get('phone', user.userprofile.phone), params.get('smart_no'),\
          params.get('customer_name'),params.get('customer_number', '-'), params.get('plan_code'), params.get('invoice', 1)
      callback_url = params.get('callback_url')

      if prevent_double.prevent_doubles(request, service, smart_no):
        return ({'status':400, 'message':'Too Immediate', 'details':'Transaction error this seems to be a duplicate request else retry in a minute'})

      # checkApiBalanceAgainstAmt(otplan_code)
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      bonuscre = BonusAccount.objects.get(user=user)
      #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
      cableApi = get_or_none(CableRecharegAPI, is_active=True, identifier=service)
      if cableApi == None:
        return Response({'status':400, 'message':'service doesnot exist'}, status=500)
      success_code = cableApi.success_code
      cableCode = json.loads(cableApi.cable_type_price)
      getCableCode = []
      for i in cableCode:
        #split the data that has the service in it and assign/make a dictionary out of it
        if otplacn_code.lower() in i.lower():
          getCableCode = i.split('|')
      # print(getplancd)
      #Get amount and system amount for the service in question
      getOtherParam = getCableCode
      ["api_code|what_user_sees|api_price|site_price|site_service_code"]
      apiamount, cable_amount, apicode, apiservicecode = getOtherParam[0],\
        getOtherParam[3], getOtherParam[2], getOtherParam[3]
      compare = float(int(cable_amount)) <= smsbal.smscredit
      old_balance = smsbal.smscredit
      act_cable_amt = float(cable_amount)
      # checkApiBalanceAgainstAmt(cable_amount)

      if compare is not True:
        return Response({'status':200, 'message':'Error', 'details': 'Insufficient Balance'}, status=200)

      from resellers.utility import ProcessUserReseller
      is_reseller = ProcessUserReseller(user, float(cable_amount), 'cable_tv', cableApi.identifier, otplacn_code)

      if is_reseller[1] is True:
        cable_amount = is_reseller[0]


      from transactions.models import Transactions

      smsbal.smscredit -= Decimal(float(cable_amount))
      smsbal.save()

      Transactions.objects.create(
          user = user,
          bill_type = "CABLE",
          #bill_code = f"{apiservicecode}|{service}|{apicode}|{apiamount}",
          bill_code = f"{apiamount}|{service}|{apiamount}|{apicode}",
          bill_number = smart_no,
          identifier = service,
          actual_amount = float(act_cable_amt),
          old_balance = old_balance,
          new_balance = smsbal.smscredit,
          paid_amount = float(cable_amount),
          status = "QUEUE",
          api_id = cableApi.id,
          reference = timezoneshit(),
          mode = "API",
          phone = phone,
          customernumber = customer_number,
          customername = customer_name,
          callback_url = callback_url
      )
      return Response({'status':201, 'message':'success', 'details': 'Transaction Submitted', 'balance': smsbal.smscredit}, status=201)
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Bad Request', 'details':' Bad Request check your paramaters'}, status=400)

@api_view(['GET'])
def listCablePlans(request):
  list_of_cable = CableRecharegAPI.objects.filter(is_active=True, api_name__icontains=request.GET.get('service'))
  serializer = CableApiSerializer(list_of_cable, many=True)
  return Response(serializer.data)
##### END CABLE API


@login_required(login_url=settings.LOGIN_URL)
def CableGotvDstvRechargeView(request):
  return Response({}, status=200)


###TRANSACTIONS FOR ALL RECHARGE APP

