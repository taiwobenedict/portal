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
import re
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
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from .views import QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication, getApiKey

from django.contrib.auth.hashers import make_password, check_password
from smsangosend.views import random_string_generator

from api.serializer import (AirtimeTopupSerializer, DataTopupSerializer, 
CableRechargeSerializer, PayStackSerializer, RefferalSerializer, RefBonusSerializer, NotificationSerializer, TransactionSerializer)
from smsangosend.tokens import TokenAuth
from vbp_helper.helpers import evalResponse
from transactions.models import Transactions


def getTheJsonRes(info, res_params):
  try:
    print(res_params, info)
    res = {}
    info = json.loads(info)
    print('info', info)
    evalRes = evalResponse(info)
    print('----', evalRes, '------', info)
    for (key, value) in evalRes.items():
      if key in res_params:
        res[key] = value
    print('res >>>', res)
    return res
  except json.decoder.JSONDecodeError:
    print('empty')
    return info

class CheckActiveDataApi(APIView):
  def get(self, request):
    dataapi = get_or_none(DataNetworks, is_active=True)
    if dataapi == None:
      return Response({'status':500, 'message':'contact the adminstrator'}, status=500)
    return Response({'status':200, 'message':'data retrieved successfully', 'apiName':dataapi.api_name}, status=200)

####API for payment from mobile 
class PaymentForMobileApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      if not user.userprofile.phone:
        return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)
      amounttobuy = params['amounttobuy']
      orderid = random_string_generator(size=20)

      from resellers.utility import IsReseller, ProcessUserReseller
      is_reseller = IsReseller(user)

      #CHECK IF USER IS A RESELLER
      if is_reseller[1] is True:
        get_min_fund = is_reseller[0][1]
        if int(amounttobuy) < get_min_fund.fund_to_wallet:
          messages.error(request, 'The minimum a {0} Reseller can fund into your wallet is NGN {1}'.format(get_min_fund.name, get_min_fund.fund_to_wallet))
          return Response({'status':'400', 'message':'The minimum a {0} Reseller can fund into your wallet is NGN {1}'.format(get_min_fund.name, get_min_fund.fund_to_wallet)}, status=403)
      else:
        pass

      if int(amounttobuy) > 2450:
        return Response({'status':'400', 'message':'The highest Amount you can pay once is #2450 per transaction'}, status=403)
      else:
        try:
          getuserspecificprice = PricingPerSMSPerUserToPurchase.objects.get(user=user)
          cedituser = getuserspecificprice.price
          context = {
            'getuserspecificprice':cedituser,
            'amounttobuy':((float(amounttobuy)*float(0.015))+float(amounttobuy))*100,
            'amounttobuyy':((float(amounttobuy)*float(0.015))+float(amounttobuy)),
            'orderid': orderid,
            'realamounttobuy': amounttobuy,
          }
          return Response({'status':201, 'message':'success', 'details':context}, status=201)
        except Exception as e:
          return Response({'status': 400, 'message':'error', 'details': 'Bad Request Check Your Parameters'}, status=400)
    except Exception as e:
      return Response({'status': 400, 'message':'error', 'details': 'Bad Request Check Your Parameters'}, status=400)
    return Response({'status': 400, 'message':'error', 'details': 'Bad Request Check Your Parameters'}, status=400)

class PaystackCallBack(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      usertocredit = getUser.user
      print(len(params))
      if len(params):
        pass
      else:
        params = json.loads(request.body)
      print(params, request.query_params, request.body, "///::::::///")
      userid = params['id']
      orderid = params['trxref']
      reference = params['reference']
      amount = params['amount']
      price = params['price']
      realamounttobuy = params['realamount']
      url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
      r = requests.get(url, auth=TokenAuth('sk_test_cfa28a9211ff6fdd35c77234a345ace2ca528f47'))
      print(r.content)
      response = json.loads(r.text)
      print(int(userid), response['data']['status'], float(realamounttobuy), float(response['data']['amount'])/100)
      if int(usertocredit.id) == int(userid) and response['data']['status'] == 'success' and float(realamounttobuy) == float(response['data']['amount'])/100:
        amountfrompayst = float(realamounttobuy)
        amtcredited = round((float(realamounttobuy)/float(price)),2)
        get_user = SmsangoSBulkCredit.objects.get(user=usertocredit)
        # print(get_user)
        obj = PayStackPayment.objects.create(
          user = usertocredit,
          smsangosbulkcredit = get_user,
          order_id = orderid,
          amtcredited = amtcredited,
          amount = realamounttobuy,
          reference = reference,
        )

        old_balance = get_user.smscredit

        # amtotcredit = float(amount)/float(price)
        updatesmscredit = float(get_user.smscredit) + float(amtcredited)
        get_user.smscredit = updatesmscredit
        get_user.save()

        payment_transaction = Transactions.objects.create(
          user = usertocredit,
          smsangosbulkcredit = get_user,
          bill_type = "PAYSTACK",
          bill_number = reference,
          reference = reference,
          amtcredited = amtcredited,
          new_balance = updatesmscredit,
          old_balance = old_balance,
          status = "SUCCESS",
          mode = "API"
        )

        request.session['amount'] = realamounttobuy
        request.session['newbalance'] = updatesmscredit
        request.session['reference'] = reference
        context = {
          'status': 200,
          'orderid':orderid,
          'amount':realamounttobuy,
          'amtotcredit':realamounttobuy,
          'updatesmscredit':updatesmscredit,
          'balance':updatesmscredit,
        }
        return Response(context, status=201)
      else:
        return Response({'status': 400, 'message':'error', 'details': 'Payment Failed'}, status=400)
    except Exception as e:
      return Response({'status': 400, 'message':'error', 'details': 'Payment Failed'}, status=400)
    return Response({'status': 400, 'message':'error', 'details': 'Payment Failed'}, status=400)


class TransactionAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      transac = Transactions.objects.filter(user=user).order_by('-created_at')[:50]
      transac = TransactionSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'transactions retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class AirtimeTransactionAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      transac = AirtimeTopup.objects.filter(user=user).order_by('-purchased_date')
      transac = AirtimeTopupSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'airtime transaction retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class DataTransactionAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = MtnDataShare.objects.filter(user=user).order_by('-purchased_date')
      transac = DataTopupSerializer(transac,many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'data transaction retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class CableTransactionAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = CableRecharge.objects.filter(user=user).order_by('-purchased_date')
      transac = CableRechargeSerializer(transac,many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'cable transaction retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class CableTransactionDetailedAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      if getUser != None:
        user = getUser.user
        getCable = CableRecharge.objects.get(user=user, ordernumber=params['transId'])

        get_res_params = CableRecharegAPI.objects.get(is_active=True, identifier=getCable.identifier).res_params
        details = getTheJsonRes(getCable.messageresp, get_res_params)

        return Response({'status':200, 'message':'cable transaction retrieve successfully', 'details': details}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class PayStackTransactionAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = PayStackPayment.objects.filter(user=user).order_by('-dated')
      transac = PayStackSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Paystack transaction retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class DoTheRedeemNowAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      redim = RedeemBonusToOcCredits(user)
      print(redim)
      if redim == 'Done':
          return Response({'status':200, 'message':'Congrats Bonus Redeemed succesfully'}, status=200)
      else:
          return Response({'status':200, 'message':'Nothing Happend'}, status=200)
      return Response({'status':200, 'message':'Nothing Happend'}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

#===========================================================31/10/19
class RefferalPageAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = UserProfile.objects.filter(refferal=user.username)
      transac = RefferalSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Referral retrieved successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class BonusPageAPI(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = RefBonusAccount.objects.filter(user=user).order_by('-updated_date')
      transac = RefBonusSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Bonuses retrieved successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class notificationsApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      params = request.query_params
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      transac = Notification.objects.filter(~Q(readonly__user__username=user.username)).order_by('-createdAt')
      transac = NotificationSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Notification Yet'}, status=200)
      return Response({'status':200, 'message':'Notifications retrieved successfully', 'details': transac.data}, status=200)
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Bad Request'}, status=400)

class readNotificationsApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      if not token:
        return Response({"details": "Cannot be authenticated"},  status=403)
      params = request.query_params
      getUser = get_or_none(Token, key=token)
      pk = params['pk']
      print(pk)
      user = getUser.user
      transacnote = get_or_none(Notification,pk=pk)
      if transacnote == None:
        return Response({'status':200, 'message':'No Notification Yet'}, status=200)
      else:
        obj = ReadNotification.objects.create(
          user = user,
          read = transacnote
        )
        transac = NotificationSerializer(transacnote)
        return Response({'status':200, 'message':'Notifications retrieved successfully', 'details': transac.data}, status=200)
    except Exception as e:
      # raise e
      return Response({'status':400, 'message':'Bad Request'}, status=400)