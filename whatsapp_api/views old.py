from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
UserModel = get_user_model() 

# Create your views here.
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.crypto import get_random_string
import requests
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.views import *
from decimal import *
from rechargeapp.models import *
from rechargeapp.utility import get_or_none
from coreconfig.models import DashboardConfig
from whatsapp_api.models import *

@csrf_exempt
def generalPostMethod(request):
  app = request.POST.get('app', None)
  if app is None:
    return JsonResponse({"reply": "Not allowed"})
  message = request.POST.get('message')
  msg = message.split(" ")
  context = {
    'message':msg,
  }
  if 'create' in msg or 'reset' in msg:
    hewd = createWhatsappPin(context)
    return JsonResponse({"reply": hewd})
  elif 'data' in msg or 'airtime' in msg:
    if msg[1].lower() == 'data':
      if msg[0].lower() == 'mtn':
        hewd = dataTopKeyword(context,'MTN')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == '9monile':
        hewd = dataTopKeyword(context,'9mobile')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == 'glo':
        hewd = dataTopKeyword(context, 'GLO')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == 'airtel':
        hewd = dataTopKeyword(context, 'Airtel')
        return JsonResponse({"reply": hewd})
    elif msg[1].lower() == 'airtime':
      if msg[0].lower() == 'mtn':
        hewd = airtimeTopUp(context,'MTN')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == '9monile':
        hewd = airtimeTopUp(context,'9mobile')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == 'glo':
        hewd = airtimeTopUp(context, 'GLO')
        return JsonResponse({"reply": hewd})
      elif msg[0].lower() == 'airtel':
        hewd = airtimeTopUp(context, 'Airtel')
        return JsonResponse({"reply": hewd})
  return JsonResponse({"reply": "Not processed"})


def airtimeTopUp(context, network):
  """network airtime username amount number_to_load pin"""
  try:
    params = context['message']
    user = get_or_none(UserModel, username=params[2].strip())
    network = network
    phone = params[4]
    amt = params[3]
    pin = params[5]

    if pin.strip() == user.user_whatsapp_access.pin and user.user_whatsapp_access.is_active == True:

      # checkApiBalanceAgainstAmt(amt)
      ordernumber = 'AT' + get_random_string(length=15)
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      old_balance = smsbal.smscredit
      bonuscre = BonusAccount.objects.get(user=user)
      #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
      compare = float(int(amt)) <= smsbal.smscredit
      if compare is True:
        getAirtimeApi = get_or_none(RechargeAirtimeAPI, is_active=True)
        if getAirtimeApi == None:
          return 'Error, not process'
        getApiUrl = getAirtimeApi.api_url
        getApiUrlData = getAirtimeApi.api_url_data
        getNetworkCodes = json.loads(getAirtimeApi.network_code_json)
        paramet = json.loads(getApiUrlData.strip())
        print(getApiUrl, getNetworkCodes)
        network_code_dis = []
        for netx in getNetworkCodes:
          if network.upper() == netx:
            network_code_dis.append(getNetworkCodes[netx])
        if len(network_code_dis) == 0 or len(network_code_dis) > 1:
          return 'Error network not found'
        network_code = network_code_dis[0].split('|')
        get_amt = int(amt) - (int(amt) * (int(network_code[1])/100))
        print(get_amt) 
        replace_keys = (('[network_code]', network_code[0]),('[phone]',phone), ('[amt]',amt))
        print(network_code)
        for (i,j) in replace_keys:
          getApiUrl = getApiUrl.replace(i,j)
          getApiUrlData = getApiUrlData.replace(i,j)
        print(getApiUrl)
        print(getApiUrlData)
        r = requests.post(getApiUrl, data=paramet['data'], headers=paramet['headers'])
        info = (r.content).decode("utf-8")
        print(info)
        #checking the API repsonse
        if getAirtimeApi.success_code in info:
          #Process if User is Reseller
          from resellers.utility import ProcessUserReseller
          is_reseller = ProcessUserReseller(user, int(amt), 'airtime', network)
          if is_reseller[1] is True:
            get_amt = is_reseller[0]

          smsbal.smscredit -= Decimal(int(get_amt))
          smsbal.save()
          AirtimeTopup.objects.create(
            user = user,
            ordernumber = ordernumber,
            recharge_amount = int(get_amt),
            recharge_number = phone,
            api_response = info,
            old_balance = float(old_balance),
            new_balance = float(smsbal.smscredit),
            recharge_network = network,
            status = "SUCCESS",
          )
          if is_reseller[1] is True:
            pass
          else:
            bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
            if bonus_to_add is None:
              pass
            else:
              getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.purchase_airtime_bonus)
              bonuscre.bonus += Decimal(getbonus_amt * float(get_amt))
              bonuscre.save()
              getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_airtime_bonus)
              getrefbonus_amt = Decimal(getrefbonus_percent * int(amt))
              CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
          return 'Airtime Transaction Successful with ID: {}'.format(ordernumber)
        else:
          return 'Airtime Transaction is not Successful'
      else:
        return 'Insufficient Balance'
    else:
      return 'Incorrect pin or user has not activated whatsapp usage\nYour Input Pattern should follow\ne.g mtn airtime username amount number pin'
  except Exception as e:
    # raise e
    return 'Bad Request Check Your Input Pattern\ne.g mtn airtime username amount number pin'


####### DATA API 

def GetTheDataValuesANDSplit():
  get_active_api = get_or_none(DataNetworks, is_active=True)
  oyaSplit = get_active_api.network_data_amount_json.split('/')
  # print(oyaSplit)
  dataNet = {}
  for x in oyaSplit:
    equalToSplit = x.split("=")
    # print(equalToSplit)
    dataNet[equalToSplit[0].lower()] = equalToSplit[1].strip().split(',')
  return dataNet

def GetPrice(data_network, data_size):
  try:
    dataNet = GetTheDataValuesANDSplit()
    # dataSizeSplit = data_size.split("|")
    getNetworkCode, getplancd = {}, {}
    for x in dataNet[data_network.lower()]:
      if data_size in x:
        getplancd['otplan_code'] = x
    getOtherParam = getplancd['otplan_code'].split('|')
    # print(getplancd)
    return getOtherParam
  except Exception as e:
    # print(e)
    return 'error'


def dataTopKeyword(context, network):
  try:
    params = context['message']
    user = get_or_none(UserModel, username=params[2].strip())
    pin = params[5]

    if pin.strip() == user.user_whatsapp_access.pin and user.user_whatsapp_access.is_active == True:

      data_network = network
      data_number = params[4]
      data_size = params[3]
      ordernumber = data_network + get_random_string(length=10)
      
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      old_balance = smsbal.smscredit
      bonuscre = BonusAccount.objects.get(user=user)
      #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
      getOtherParam = GetPrice(data_network, data_size)
      apiamount, data_amount, apicode, urlvariable = getOtherParam[0],\
        getOtherParam[1], getOtherParam[2], getOtherParam[3]
      compare = float(data_amount) <= smsbal.smscredit
      # checkApiBalanceAgainstAmt(data_amount)
      if compare is True:
        dataapi = get_or_none(DataNetworks, is_active=True, identifier="")
        if dataapi == None:
          return 'contact the adminstrator'
        getApiUrl = dataapi.api_url
        getApiUrlData = dataapi.api_url_data
        replace_keys = (('[network_code]', apicode),('[phone]',data_number), ('[dataplan]',data_size),\
          ('[apiamount]', apiamount), ('[urlvariable]', urlvariable),\
          ('[network]', data_network))
        for (i,j) in replace_keys:
          getApiUrl = getApiUrl.replace(i,j)
          getApiUrlData = getApiUrlData.replace(i,j)
        paramet = json.loads(getApiUrlData.strip())
        r = requests.post(getApiUrl, data=paramet['data'], headers=paramet['headers'])
        # print(getApiUrl, paramet['data'], paramet['headers'])
        info = (r.content).decode("utf-8")
        # info = ("true")
        # print(info)
        #checking the API repsonse
        if dataapi.success_code in str(info):
          #Process if User is Reseller
          from resellers.utility import ProcessUserReseller
          is_reseller = ProcessUserReseller(user, data_amount, 'data', data_network)
          if is_reseller[1] is True:
            data_amount = is_reseller[0]

          smsbal.smscredit -= Decimal(int(data_amount))
          smsbal.save()
          obj = MtnDataShare.objects.create(
            user = user,
            ordernumber = ordernumber,
            data_amount = int(data_amount),
            dataSize = data_size,
            data_number = data_number,
            data_network = data_network,
            batchno = ordernumber,
            api_response = info,
            old_balance = float(old_balance),
            new_balance = float(smsbal.smscredit),
            status = "SUCCESS",
          )
          if is_reseller[1] is True:
            pass
          else:
            bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
            if bonus_to_add is None:
              pass
            else:
              getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.purchase_data_bonus)
              bonuscre.bonus += Decimal(getbonus_amt * float(data_amount))
              bonuscre.save()
              getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_data_bonus)
              getrefbonus_amt = Decimal(getrefbonus_percent * float(data_amount))
              CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
          return 'Data Transaction Successful with ID {}'.format(ordernumber)
        else:
          return 'Data Transaction is not Successful'
      else:
        return 'Insufficient Balance'
    else:
      return 'Incorrect pin or user has not activated whatsapp usage\nYour Input Pattern should follow\ne.g mtn data username datacode number pin'
  except Exception as e:
    # print(e)
    return 'Bad Request Check Your Input Pattern\ne.g mtn data username data_size number pin'

from coreconfig.models import *
def createWhatsappPin(context):
  params = context['message']
  try:
    user = get_or_none(UserModel, username=params[1])
    chk_whats_user = get_or_none(WhatsAppPurchaseAccess, user=user)
    if user != None:
      if params[0] == 'create':
        if chk_whats_user is None:
          what_user = WhatsAppPurchaseAccess.objects.create(user=user, pin=get_random_string(length=6, allowed_chars='1234567890'), is_active=True)
          return '*{}* \nis your pin\nplease keep but delete from your whatsapp history'.format(what_user.pin)
        else:
          return 'Whatsapp purchase access has been previously created, use your pin to purchase or reset your pin with \n\n"reset username old-pin"'
      elif params[0] == 'reset':
        what_user = WhatsAppPurchaseAccess.objects.get(user=user, is_active=True)
        if what_user.pin == params[2]:
          what_user.pin = get_random_string(length=6, allowed_chars='1234567890')
          what_user.save()
          return '*{}* \nis your new pin\nplease keep but delete from your whatsapp history'.format(what_user.pin)
        else:
          return 'Pin is incorrect'
    else:
      return 'Nothing was done'
  except Exception as e:
    config = DashboardConfig.objects.all()
    if len(config) >= 1:
      return 'Something went wrong contact the admin on {}'.format(config[0].phone)
    return 'Something went wrong contact the admin'