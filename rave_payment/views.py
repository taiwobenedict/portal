from django.shortcuts import render
#ALL ADMIN VIEWS ARE NEEDED
import re, os, requests, datetime, random, string, subprocess
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

from django.http import HttpResponse, HttpResponseRedirect
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
from rave_payment.models import *
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import *
from smsangonumcredit.views import *
from decimal import *
UserModel = get_user_model() 

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url=settings.LOGIN_URL)
def FlutterPaymentPage(request):
	#IMPORT RESELLER PACKAGE
	# from resellers.utility import IsReseller, ProcessUserReseller 

	template_name = 'rave/payment_page.html'
	user=request.user

	# is_reseller = IsReseller(user)

	if not user.userprofile.phone:
		return HttpResponseRedirect('/customer/profile-edit')	
	if request.method=="POST":
		amounttobuy = request.POST.get('amounttobuy')
		orderid = random_string_generator(size=20)

		#CHECK IF USER IS A RESELLER
		# if is_reseller[1] is True:
		# 	get_min_fund = is_reseller[0][1]
		# 	if int(amounttobuy) < get_min_fund.fund_to_wallet:
		# 		messages.error(request, 'The minimum a {0} Reseller can fund into your wallet is NGN {1}'.format(get_min_fund.name, get_min_fund.fund_to_wallet))
		# 		return redirect('smsangosend:toenteramount')
		# else:
		# 	pass
		
		dash = RaveConfiguration.objects.all()[0]
		if int(amounttobuy) > dash.funding_limit:
			messages.error(request, 'The highest Amount you can pay once is {} per transaction'.format(dash.funding_limit))
			return redirect('smsangosend:toenteramount')
		else:
			try:
				getuserspecificprice = PricingPerSMSPerUserToPurchase.objects.get(user=user)
				cedituser = getuserspecificprice.price
				context = {
					'getuserspecificprice':cedituser,
					'amounttobuy':((float(amounttobuy)*float(dash.rave_fee))+float(amounttobuy)),
					'amounttobuyy':((float(amounttobuy)*float(dash.rave_fee))+float(amounttobuy)),
					'orderid': orderid,
					'realamounttobuy': amounttobuy,
          'funding_fee': dash.rave_fee,
          'public_key': dash.public_key,
				}
				return render(request, template_name, context)
			except ObjectDoesNotExist:
				getdefaultprice = DefaultPricePerSMSToPurchase.objects.get(is_active=True)

				context = {
					'getuserspecificprice':float(getdefaultprice.priceperunit),
					'amounttobuy':((float(amounttobuy)*float(dash.rave_fee))+float(amounttobuy)),
					'amounttobuyy':((float(amounttobuy)*float(dash.rave_fee))+float(amounttobuy)),
					'orderid': orderid,
					'realamounttobuy': amounttobuy,
          'funding_fee': dash.rave_fee,
          'public_key': dash.public_key,
				}
				return render(request, template_name, context)
		return render(request, template_name)
	return render(request, template_name)

from .tokens import TokenAuth
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
def RaveSuccess(request):
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
def RaveCallBack(request):
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

  url = 'https://api.flutterwave.com/v3/transactions/{}/verify'.format(tansaction_id)
  r = requests.get(url, auth=TokenAuth(RaveConfiguration.objects.all()[0].secret_key))
  print(r.content)
  response = json.loads(r.text)
  if int(usertocredit.id) == int(userid) and response['data']['status'] == 'successful' and response['status'] == 'success' and float(response['data']['amount']) == float(amount):
    print(response['data']['amount'] == amount,  response['data']['amount'], amount)
    amountfrompayst = float(realamounttobuy)
    amtcredited = round((float(realamounttobuy)/float(price)),2)
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
			'status': response['data']['status'],
			'orderid':orderid,
			'amount':realamounttobuy,
			'amtotcredit':realamounttobuy,
			'updatesmscredit':updatesmscredit,
		}
    return JsonResponse(context, safe=False)
  else:
    return JsonResponse({'error': 'failed'}, safe=False)
  return JsonResponse({'error': 'failed'}, safe=False)