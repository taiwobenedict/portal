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
import re, json
import requests, datetime
from django.utils.crypto import get_random_string
# from datetime import 
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.loader import render_to_string
from django.views import generic
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
from .views import QueryStringBasedTokenAuthentication, HeaderBasedTokenAuthentication

from django.contrib.auth.hashers import make_password, check_password
from smsangosend.views import random_string_generator
from external_cron.views import SMSTask
from smsangosend.tasks import send_bulk_sms_bg, SendScheduledSMS_bg

from api.serializer import (SmsHistorySerializer)
from monnify.monnify import Monnify
from api.models import KycApi

#SEND SMS VIEW CODED#################
class SmsangoSendSMSApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      if not user.userprofile.phone:
        return Response({'status':'403', 'message': 'Update your profile to proceed'}, status=403)
      successde = None
      sender = params["sender"]
      recipients = params["recipients"]
      messagecontent = params["messagecontent"]
      smsroute = params["smsroute"]
      smsroute = getApiObject(smsroute)
      if isinstance(smsroute, dict) is False:
        messages.warning(request, smsroute)
        return Response({'status':400, 'message':'Error', 'details':smsroute}, status=200)
      opages = getMsgContent(messagecontent)
      if opages > 3:
        return Response({'status':400, 'message':'Error', 'details':"Message content more that 480 characters"}, status=200)
      numcount = recipients.split(',')
      numlength = len(numcount)
      if numlength > 100:
        return Response({'status':400, 'message':'Error', 'details':"You cant send to more than 100 at once"}, status=200)
      totalsms = (numlength * smsroute['apiamtpersms'] * opages)
      rt = SmsangoSBulkCredit.objects.get(user=user)
      
      if int(totalsms) > int(rt.smscredit):
        successde = "You are low on credit, purchase sms units to send sms" 
        return Response({'status':400, 'message':'Error', 'details':successde}, status=200)
      else:
        SMSTask('smsangosend.tasks.send_bulk_sms_bg', {
          'userid':user.id,
					'sender':sender,
					'recipients':recipients,
					'numcount':numcount,
					'messagecontent':messagecontent,
					'smsroute':smsroute,
					'totalsms':totalsms,
					'opages':opages
				})
        successde = str(numlength) + " Messages are being sent in background Check SMS Report for full details"
        return Response({'status':200, 'message':'success', 'details':successde}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)
    return Response({'status':400, 'message':'Bad Request'}, status=400)

class smsHistoryApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      user = getUser.user
      transac = SmsangoSendSMS.objects.filter(user=user).order_by('-timestamp')
      transac = SmsHistorySerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No SMS Sent Yet'}, status=200)
      return Response({'status':200, 'message':'SMS Messages retrieve successfully', 'details': transac.data}, status=200)
    except Exception as e:
      raise e
      return Response({'status':400, 'message':'Bad Request'}, status=400)
    return Response({'status':400, 'message':'Bad Request'}, status=400)

class singleSmsHistoryApi(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      getUser = get_or_none(Token, key=params['api-token'])
      pk = params['pk']
      print(pk)
      user = getUser.user
      transacSMS = get_or_none(SmsangoSendSMS,pk=pk)
      if transacSMS == None:
        return Response({'status':200, 'message':'No messages'}, status=200)
      transac = SmsHistorySerializer(transacSMS)
      return Response({'status':200, 'message':'SMS messages retrieved successfully', 'details': transac.data}, status=200)
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'}, status=400)
    return Response({'status':400, 'message':'Bad Request'}, status=400)


def flatten_dict(dictionary, parent_key='', separator='.'):
    flattened_dict = {}
    for key, value in dictionary.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, separator))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


def format_numbers(one, two):
  if one:
    return "234" + one[1:11]
  if two:
    return "234" + two[1:11]

class DoKycVerification(APIView):
  authentication_classes = (HeaderBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      user = request.user
      userprofile = user.userprofile
      body = json.loads(request.body)
      nin = body.get('nin')
      kyc_type = body['kyc_type']
      code = body.get("code")
      resend = body.get("resend")

      if resend:
        try:
          url = request.session[f"sms_url{user.id}"]
          inf = requests.get(url, headers={})
          if "OK" in str(inf.content):
            return Response({'status':201, 'message':'Success', 'details': 'Otp has been sent to your bvn phone number'}, status=201)
          return Response({'status':400, 'message':'Success', 'details': 'Otp has been resent to your bvn phone number'}, status=400)
        except:
          return Response({'status':400, 'message':'Success', 'details': 'Otp has been resent to your bvn phone number'}, status=400)

      if code:
        print(request.session[f"bvn_validation_user{user.id}"],'request.session[f"bvn_validation_user{user.id}"]')
        if code == request.session[f"bvn_validation_user{user.id}"]:
          #update this after the user has sent  the otp.
          userprofile.bvn_kyc = request.session[f"bvn_validation_user{user.id}nin"]
          userprofile.kyc_verification = True
          userprofile.save()
          return Response({'status':201, 'message':'Success', 'details': 'Verification Successful'}, status=201)
        else:
          return Response({'status':400, 'message':'Failed', 'details': 'Verification Failed'}, status=400)

      #clear code
      try:
        del request.session[f"bvn_validation_user{user.id}"]
        del request.session[f"bvn_validation_user{user.id}nin"]
      except:
        pass

      kyc_api = get_object_or_404(KycApi, is_active=True, kyc_type=kyc_type)

      print(kyc_api)

      if kyc_api and not kyc_api.do_verifcation:
        if kyc_api.kyc_type == "BVN":
          userprofile.bvn_kyc = nin
          userprofile.save()
        if kyc_api.kyc_type == "NIN":
          userprofile.nin_kyc = nin
          userprofile.save()
        return Response({'status':201, 'message':'Success', 'details': 'Saved Successfully'}, status=201)

      #deduct the kyc money from user
      wallet = user.smsbulkcredit
      old_balance = wallet.smscredit
      wallet.smscredit -= Decimal(kyc_api.kyc_cost)
      wallet.save()

      #save to paystack
      ref = "kyc" + get_random_string(length=10)
      PayStackPayment.objects.create(
        user = user,
        smsangosbulkcredit = user.smsbulkcredit,
        order_id = ref,
        amtcredited = kyc_api.kyc_cost,
        amount = kyc_api.kyc_cost,
        reference = ref,
        reason = f"Paid for Kyc verification ({kyc_type})",
        action = "SUCCESS",
        old_balance = float(old_balance),
        new_balance = float(wallet.smscredit),
      )

      url = (kyc_api.url).strip()
      url_data = kyc_api.url_data
      replace_keys = (('[NIN]',nin))
      url = url.replace('[NIN]',nin)
      url_data = str(url_data).replace('[NIN]',nin)
      paramet = ast.literal_eval(url_data)
      # print(url)

      from vbp_helper.request_method import call_external_api
      info = call_external_api(url, paramet['data'], paramet['headers'])

      # print(info, "info")

      if any(respo in str(info) for respo in kyc_api.success_code.split(",")):

        # # check if the info has the firstname and last name
        # if any(respo in str(info) for respo in [user.first_name, user.last_name]):

        new = flatten_dict(json.loads(info))
        print(new)

        if kyc_type == "NIN":
          if any(respo in str(info) for respo in [user.first_name, user.last_name]):
            userprofile.nin_kyc = nin
            userprofile.kyc_verification_nin = True
            userprofile.verication_response_nin = str(info)
            userprofile.save()

            return Response({'status':201, 'message':'Success', 'details': 'Verification Successful'}, status=201)
          else:
            return Response({'status':400, 'message':'Failed', 'details': 'Verification Failed First and lastname does not match the profile'}, status=400)

        
        if kyc_type == "BVN" and (new.get("entity.phone_number1") or new.get("entity.phone_number2")):
          print("hellor", new.get("entity.phone_number1"))
          #send sms to bvn number
          code = get_random_string(length=4, allowed_chars='1234567890')
          message = f"Use {code} One time code to complete your verification on paytev"
          sms_url = kyc_api.sms_url.replace("[MESSAGE]", message)
          sms_url = sms_url.replace("[NUMBER]", format_numbers(new.get("entity.phone_number1"), new.get("entity.phone_number2")))
          
          request.session[f"sms_url{user.id}"] = sms_url

          inf = requests.get(sms_url, headers={})
          print(inf.content, "inf")

          request.session[f"bvn_validation_user{user.id}"] = code
          request.session[f"bvn_validation_user{user.id}nin"] = nin
          if "OK" in str(inf.content):

            userprofile.verification_response = str(info)
            userprofile.save()
            return Response({'status':201, 'message':'Success', 'details': 'Otp has been sent to your bvn phone number'}, status=201)

          return Response({'status':400, 'message':'Failed', 'details': 'Sms failed to send'}, status=400)
      return Response({'status':400, 'message':'Failed', 'details': 'Verification Failed'}, status=400)
    except Exception as e:
      return Response({'status':400, 'message':'Error', 'details': f'Contact the Administrator {e}'}, status=400)    
