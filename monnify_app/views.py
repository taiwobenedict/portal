from django.shortcuts import render, redirect, reverse
#ALL ADMIN VIEWS ARE NEEDED
# Create your views here.
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
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView

import requests, datetime, random, re, json
from re import template

from django.contrib.auth.models import User
from payments.models import *
from rechargeapp.models import AirtimeTopup,CableRecharge,DataPlansPrices,BonusAccount,MtnDataShare
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import *
from smsangonumcredit.views import *
from decimal import *
from django.views.decorators.csrf import csrf_exempt
UserModel = get_user_model() 
from monnify.monnify import Monnify
from monnify_app.models import *
from coreconfig.models import DashboardConfig
import string

from .monnify_over import MonnifyV2
# @login_required(login_url=settings.LOGIN_URL)
# def MonnifyAccountReservation(request):
#   user = request.user
#   monnifykeys = MonnifyKeys.objects.all()
#   chkIf = get_or_none(MonnifyAccount, user=user)
#   try:
#     if chkIf == None:
#       if len(monnifykeys) == 0:
#         return JsonResponse({
#             'status': 400,
#             'message': 'Unique Account Generator API not Activated Yet',
#           })
#       else:
#         apiKey = monnifykeys[0].apiKey
#         clientSecret = monnifykeys[0].clientSecret
#         gmonnify = Monnify(apiKey, clientSecret)

#         accRef = 'Acc' + get_random_string(length=14)

#         createReserveAcc = gmonnify.createReserveAccount(
#           accRef,
#           user.username + ' ' + get_random_string(length=3) + ' ' + DashboardConfig.objects.first().site_domain,
#           monnifykeys[0].currencyCode,
#           monnifykeys[0].contractCode,
#           user.email,
#           user.get_full_name()
#         )

#         print(createReserveAcc)

#         if createReserveAcc['responseMessage'] == 'success' and createReserveAcc['responseCode'] == "0":

#           c = createReserveAcc['responseBody']

#           saveAccToDb = MonnifyAccount.objects.create(user=user)
#           saveAccToDb.accountReference = c['accountReference']
#           saveAccToDb.accountName = c['accountName']
#           saveAccToDb.currencyCode = c['currencyCode']
#           saveAccToDb.customerEmail = c['customerEmail']
#           saveAccToDb.accountNumber = c['accountNumber']
#           saveAccToDb.bankName = c['bankName']
#           saveAccToDb.bankCode = c['bankCode']
#           saveAccToDb.reservationReference = c['reservationReference']
#           saveAccToDb.status = c['status']

#           saveAccToDb.save()

#           return JsonResponse({
#             'status': 201,
#             'message': 'Unique Account Number Generated Successfully',
#           })
#         else:
#           return JsonResponse({
#             'status': 400,
#             'message': 'Error Gnerating account, try again!!!',
#           })
#   except Exception as e:
#     return JsonResponse({
#       'status': 201,
#       'message': 'Something Went Wrong, when creating the account, contact the site Administrator',
#     })

#   return JsonResponse({
#     'status': 400,
#     'message': 'Something Went Wrong!!'
#   })

def UpdateAccountReservationBvn(user):
  monnifykeys = MonnifyKeys.objects.all()
  chkIf = get_or_none(MonnifyAccount, user=user)
  try:
    if chkIf == None:
      if len(monnifykeys) == 0:
        return False
      else:
        apiKey = monnifykeys[0].apiKey
        clientSecret = monnifykeys[0].clientSecret
        gmonnify = MonnifyV2(apiKey, clientSecret)

        acct_v2 = MonnifyAccount.objects.get(user=user)

        reserve_account_data = {
            'accountReference': acct_v2.accountReference
        }

        if user.userprofile.bvn_kyc:
          reserve_account_data["bvn"] = user.userprofile.bvn_kyc
        if user.userprofile.nin_kyc:
          reserve_account_data["nin"] = user.userprofile.nin_kyc

        createReserveAcc = gmonnify.updateBvnNin(
          **reserve_account_data
        )

        print(createReserveAcc)

        if createReserveAcc['responseMessage'] == 'success' and createReserveAcc['responseCode'] == "0":
          return True
        else:
          return False
  except Exception as e:
    return False

  return False

def FMonnifyAccountReservation(user):
  monnifykeys = MonnifyKeys.objects.all()
  chkIf = get_or_none(MonnifyAccount, user=user)
  try:
    if chkIf == None:
      if len(monnifykeys) == 0:
        return False
      else:
        apiKey = monnifykeys[0].apiKey
        clientSecret = monnifykeys[0].clientSecret
        gmonnify = MonnifyV2(apiKey, clientSecret)

        accRef = 'Acc' + get_random_string(length=14)

        reserve_account_data = {
            'accountReference': accRef,
            'accountName': user.get_full_name(),
            'currencyCode': monnifykeys[0].currencyCode,
            'contractCode': monnifykeys[0].contractCode,
            'customerEmail': user.email,
            'customerName': user.get_full_name(),
            'getAllAvailableBanks': True,
        }

        if user.userprofile.bvn_kyc:
          reserve_account_data["bvn"] = user.userprofile.bvn_kyc
        if user.userprofile.nin_kyc:
          reserve_account_data["nin"] = user.userprofile.nin_kyc

        createReserveAcc = gmonnify.createReserveAccountV3(
          **reserve_account_data
        )

        print(createReserveAcc)

        if createReserveAcc['responseMessage'] == 'success' and createReserveAcc['responseCode'] == "0":

          c = createReserveAcc['responseBody']

          bankName, bankCode, accountNumber = [], [], []
          for acc in c['accounts']:
            bankName.append(acc['bankName'])
            bankCode.append(acc['bankCode'])
            accountNumber.append(acc['accountNumber'])

          saveAccToDb = MonnifyAccount.objects.create(user=user)
          saveAccToDb.accountReference = c['accountReference']
          saveAccToDb.accountName = c['accountName']
          saveAccToDb.currencyCode = c['currencyCode']
          saveAccToDb.customerEmail = c['customerEmail']
          saveAccToDb.accountNumber = " | ".join(accountNumber)
          saveAccToDb.bankName = " | ".join(bankName)
          saveAccToDb.bankCode = " | ".join(bankCode)
          saveAccToDb.reservationReference = c['reservationReference']
          saveAccToDb.status = c['status']

          saveAccToDb.save()

          return True
        else:
          return False
  except Exception as e:
    return False

  return False


@login_required(login_url=settings.LOGIN_URL)
def MonnifyAccountReservation(request):
  user = request.user
  monnifykeys = MonnifyKeys.objects.all()
  chkIf = get_or_none(MonnifyAccount, user=user)
  try:
    if chkIf == None:
      if len(monnifykeys) == 0:
        return JsonResponse({
            'status': 400,
            'message': 'Unique Account Generator API not Activated Yet',
          })
      elif not user.first_name or not user.last_name:
        return JsonResponse({
          'status': 400,
          'message': 'Update your profile, firstname and last name missing',
          'redirect': True,
        })
      else:
        apiKey = monnifykeys[0].apiKey
        clientSecret = monnifykeys[0].clientSecret
        gmonnify = MonnifyV2(apiKey, clientSecret)

        accRef = 'Acc' + get_random_string(length=14)

        reserve_account_data = {
            'accountReference': accRef,
            'accountName': user.get_full_name(),
            'currencyCode': monnifykeys[0].currencyCode,
            'contractCode': monnifykeys[0].contractCode,
            'customerEmail': user.email,
            'customerName': user.get_full_name(),
            'getAllAvailableBanks': True,
        }

        if user.userprofile.bvn_kyc:
          reserve_account_data["bvn"] = user.userprofile.bvn_kyc
        if user.userprofile.nin_kyc:
          reserve_account_data["nin"] = user.userprofile.nin_kyc

        createReserveAcc = gmonnify.createReserveAccountV3(
          **reserve_account_data
        )

        print(createReserveAcc)

        if createReserveAcc['responseMessage'] == 'success' and createReserveAcc['responseCode'] == "0":

          c = createReserveAcc['responseBody']

          bankName, bankCode, accountNumber = [], [], []
          for acc in c['accounts']:
            bankName.append(acc['bankName'])
            bankCode.append(acc['bankCode'])
            accountNumber.append(acc['accountNumber'])

          saveAccToDb = MonnifyAccount.objects.create(user=user)
          saveAccToDb.accountReference = c['accountReference']
          saveAccToDb.accountName = c['accountName']
          saveAccToDb.currencyCode = c['currencyCode']
          saveAccToDb.customerEmail = c['customerEmail']
          saveAccToDb.accountNumber = " | ".join(accountNumber)
          saveAccToDb.bankName = " | ".join(bankName)
          saveAccToDb.bankCode = " | ".join(bankCode)
          saveAccToDb.reservationReference = c['reservationReference']
          saveAccToDb.status = c['status']

          saveAccToDb.save()

          return JsonResponse({
            'status': 201,
            'message': 'Unique Account Number Generated Successfully',
          })
        else:
          return JsonResponse({
            'status': 400,
            'message': 'Error Gnerating account, try again!!!',
          })
  except Exception as e:
    return JsonResponse({
      'status': 201,
      'message': 'Something Went Wrong, when creating the account, contact the site Administrator',
    })

  return JsonResponse({
    'status': 400,
    'message': 'Something Went Wrong!!'
  })


@csrf_exempt
def MonnifyAccountNotification(request):
  if request.method == 'POST':
    body = request.body
    # print(body)
    try:
      req = json.loads(body.decode('utf8'))
      if req["eventType"] != "SUCCESSFUL_TRANSACTION":
        return JsonResponse({'status':400, 'message': 'Not done'})
      
      req = req['eventData']
      transactionReference = req['transactionReference']
      paymentReference = req['paymentReference']
      amountPaid = req['amountPaid']
      paidOn = req['paidOn']
      # transactionHash = req['transactionHash']
      productReference = req['product']['reference']
      email = req['customer']['email']
      name = req['customer']['name']

      piy = req["paymentSourceInformation"][0]

      # paymentStatus = req['paymentStatus']
      # paymentDescription = req['paymentDescription']
      # totalPayable = req['totalPayable']
      # settlementAmount = req['settlementAmount']
      # currency = req['currency']
      # paymentMethod = req['paymentMethod']
      # productType = req['product']['type']

      """Compare generated hash with hash from monnify"""
      monnifykeys = MonnifyKeys.objects.all()
      apiKey = monnifykeys[0].apiKey
      clientSecret = monnifykeys[0].clientSecret
      fee = monnifykeys[0].fee
      maxAmt = monnifykeys[0].maxAmountToDeductFee
      maxFee = monnifykeys[0].maxAmountFeeToDeduct

      gmonnify = Monnify(apiKey, clientSecret)
      # hashed_value = gmonnify.createHashFromWebhook(
      #   paymentReference,
      #   amountPaid,
      #   paidOn,
      #   transactionReference
      # )

      verifyTrans = gmonnify.getTranasactionDetails(transactionReference)
      print(verifyTrans)
      if verifyTrans['responseMessage'] == 'success' and verifyTrans['responseBody']['paymentStatus'] == 'PAID':
        chkPaymentDb = get_or_none(PayStackPayment, order_id=transactionReference, reference=transactionReference)
        if chkPaymentDb != None:
          return JsonResponse({'status':200, 'message': 'Processed Before'})
        else:
          compareAccRef = productReference == verifyTrans['responseBody']['product']['reference']
          compareEmail = email == verifyTrans['responseBody']['customer']['email']
          compareName = name == verifyTrans['responseBody']['customer']['name']
          getuser = MonnifyAccount.objects.get(accountReference=verifyTrans['responseBody']['product']['reference'])
          smsangosbulkcredit = SmsangoSBulkCredit.objects.get(user=getuser.user)
          old_balance = smsangosbulkcredit.smscredit
          if compareAccRef is True and compareEmail is True and compareName is True:

            """Account crediting"""
            if maxAmt > float(amountPaid):
              updatesmscredit = float(smsangosbulkcredit.smscredit) + (float(amountPaid) - (float(amountPaid) * fee))
              smsangosbulkcredit.smscredit = updatesmscredit
              smsangosbulkcredit.save()

              PayStackPayment.objects.create(
                user=getuser.user,
                smsangosbulkcredit=smsangosbulkcredit,
                order_id=transactionReference,
                reference=paymentReference,
                amtcredited=(float(amountPaid) - (float(amountPaid) * fee)),
                amount=(float(amountPaid) - (float(amountPaid) * fee)),
                old_balance=float(old_balance),
                new_balance=float(smsangosbulkcredit.smscredit),
                reason = f"Source: {piy.get('accountName')} | {piy.get('accountNumber')} | {piy.get('sessionId')} | {piy.get('bankCode')}"
              )

            else:
              updatesmscredit = float(smsangosbulkcredit.smscredit) + (float(amountPaid) - maxFee)
              smsangosbulkcredit.smscredit = updatesmscredit
              smsangosbulkcredit.save()

              PayStackPayment.objects.create(
                user=getuser.user,
                smsangosbulkcredit=smsangosbulkcredit,
                order_id=transactionReference,
                reference=paymentReference,
                amtcredited=(float(amountPaid) - maxFee),
                amount=(float(amountPaid) - maxFee),
                old_balance=float(old_balance),
                new_balance=float(smsangosbulkcredit.smscredit),
                reason = f"Source: {piy.get('accountName')} | {piy.get('accountNumber')} | {piy.get('sessionId')} | {piy.get('bankCode')}"
              )
            
            # print('Success')
            return JsonResponse({'status':200, 'message': 'Done'})
    except Exception as e:
      # print('not done')
      return JsonResponse({'status':400, 'message': 'Not done'})
  else:
    # print('error')
    return JsonResponse({'error': "eROOR"})



@login_required(login_url=settings.LOGIN_URL)
def MonnifyPaymentPage(request):
  mobile = request.GET.get("mobile")
  #IMPORT RESELLER PACKAGE
  from resellers.utility import IsReseller, ProcessUserReseller 

  template_name = 'monnify_app/payment_page.html' if not mobile else 'mobile/funding/monnify.html'
  user=request.user

  is_reseller = IsReseller(user)

  if not user.userprofile.phone:
    return HttpResponseRedirect('/customer/profile-edit') 
  if request.method=="POST":
    def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
      return ''.join(random.choice(chars) for _ in range(size))
    amounttobuy = request.POST.get('amounttobuy')
    orderid = random_string_generator(size=20)

    #CHECK IF USER IS A RESELLER
    if is_reseller[1] is True:
      get_min_fund = is_reseller[0][1]
      if int(amounttobuy) < get_min_fund.fund_to_wallet:
        messages.error(request, 'The minimum a {0} Reseller can fund into your wallet is NGN {1}'.format(get_min_fund.name, get_min_fund.fund_to_wallet))
        return redirect('smsangosend:toenteramount')
    else:
      pass
    
    monnifykeys = MonnifyKeys.objects.all()
    apiKey = monnifykeys[0].apiKey
    clientSecret = monnifykeys[0].clientSecret
    if int(amounttobuy) > 10000:
      messages.error(request, 'The highest Amount you can pay once is {} per transaction'.format(monnifykeys[0].monnify_card_funding_limit))
      return redirect('smsangosend:toenteramount')
    else:
      try:
        getuserspecificprice = PricingPerSMSPerUserToPurchase.objects.get(user=user)
        cedituser = getuserspecificprice.price
        context = {
          'getuserspecificprice':cedituser,
          'amounttobuy':((float(amounttobuy)*float(monnifykeys[0].fee))+float(amounttobuy)),
          'amounttobuyy':((float(amounttobuy)*float(monnifykeys[0].fee))+float(amounttobuy)),
          'orderid': orderid,
          'realamounttobuy': amounttobuy,
          'funding_fee': monnifykeys[0].monnify_card_fee,
          'public_key': apiKey,
          'contractCode': monnifykeys[0].contractCode
        }
        print(context, "context ==> 1")
        return render(request, template_name, context)
      except ObjectDoesNotExist:
        getdefaultprice = DefaultPricePerSMSToPurchase.objects.get(is_active=True)

        context = {
          'getuserspecificprice':float(getdefaultprice.priceperunit),
          'amounttobuy':((float(amounttobuy)*float(monnifykeys[0].fee))+float(amounttobuy)),
          'amounttobuyy':((float(amounttobuy)*float(monnifykeys[0].fee))+float(amounttobuy)),
          'orderid': orderid,
          'realamounttobuy': amounttobuy,
          'funding_fee': monnifykeys[0].monnify_card_fee,
          'public_key': apiKey,
          'contractCode': monnifykeys[0].contractCode
        }
        print(context, "context ==> 2")
        return render(request, template_name, context)
    return render(request, template_name)
  return render(request, template_name)

from rave_payment.tokens import TokenAuth
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
def MonnifySuccess(request):
	amountfrompayst = request.session['amount']
	updatesmscredit = request.session['newbalance']
	reference = request.session['reference']
	template_name = 'paystack/success_page.html'
	context = {
		'amountfrompayst':amountfrompayst,
		'reference': reference,
		'updatesmscredit': updatesmscredit
	}
	return render(request, template_name, context)

@login_required(login_url=settings.LOGIN_URL)
def MonnifyCallBack(request):
  try:
    usertocredit = request.user
    userid = request.POST['id']
    tansaction_id = request.POST['transaction_id']
    orderid = request.POST['trxref']
    reference = request.POST['reference']
    amount = request.POST['amount']
    price = request.POST['price']
    realamounttobuy = request.POST['realamount']

    get_trans = PayStackPayment.objects.filter(order_id=orderid, reference=reference)
    if get_trans.count() > 0:
      print(get_trans.count())
      return JsonResponse({'error': 'Transaction has been processed before'}, safe=False)

    monnifykeys = MonnifyKeys.objects.all()
    apiKey = monnifykeys[0].apiKey
    clientSecret = monnifykeys[0].clientSecret
    fee = monnifykeys[0].fee
    maxAmt = monnifykeys[0].maxAmountToDeductFee
    maxFee = monnifykeys[0].maxAmountFeeToDeduct

    gmonnify = Monnify(apiKey, clientSecret)
    verifyTrans = gmonnify.getTranasactionDetails(tansaction_id)
    print(verifyTrans, realamounttobuy)
    response = verifyTrans
    if int(usertocredit.id) == int(userid) and response['requestSuccessful'] is True and response['responseBody']['paymentStatus'] == 'PAID' and float(response['responseBody']['amountPaid']) == float(amount):
      amountfrompayst = float(response['responseBody']['amountPaid'])
      amtcredited = round((float(amountfrompayst)/float(price)),2)
      get_user = SmsangoSBulkCredit.objects.get(user=usertocredit)
      old_balance = get_user.smscredit

      obj_pay = PayStackPayment.objects.create(
  			user = usertocredit,
  			smsangosbulkcredit = get_user,
  			order_id = orderid,
  			amtcredited = amtcredited,
  			amount = realamounttobuy,
  			reference = reference,
  			old_balance = float(old_balance),
        reason = f"Source: Card via monnify"
  		)
      
      updatesmscredit = float(get_user.smscredit) + float(amtcredited)
      get_user.smscredit = updatesmscredit
      get_user.save()
      
      obj_pay.new_balance = float(get_user.smscredit)
      obj_pay.save()
  		
      request.session['amount'] = realamounttobuy
      request.session['newbalance'] = updatesmscredit
      request.session['reference'] = reference
      context = {
  			'status': response['responseMessage'],
  			'orderid':orderid,
  			'amount':realamounttobuy,
  			'amtotcredit':realamounttobuy,
  			'updatesmscredit':updatesmscredit,
  		}
      return JsonResponse(context, safe=False)
    else:
      return JsonResponse({'error': 'failed'}, safe=False)
  except:
    return JsonResponse({'error': 'failed'}, safe=False)
  return JsonResponse({'error': 'failed'}, safe=False)

