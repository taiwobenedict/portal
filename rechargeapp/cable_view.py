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
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView

import datetime, random, re
from re import template

import json
from django.contrib.auth.models import User
from payments.models import *
from rechargeapp.models import CableRecharegAPI,DataNetworks,RechargeAirtimeAPI,AirtimeTopup,CableRecharge,DataPlansPrices,BonusAccount,MtnDataShare
from rechargeapp.utility import get_or_none
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.views import *
from smsangonumcredit.models import *
from decimal import *
UserModel = get_user_model() 
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from vbp_helper.helpers import evalResponse, timezoneshit
import ast
from django.views.decorators.cache import cache_control, never_cache
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
  except json.decoder.JSONDecodeError:
    # print('empty')
    return info

@login_required(login_url=settings.LOGIN_URL)
def cableTemplate(request):
    template_name = "general/general_layout.html"
    api_obj = CableRecharegAPI.objects.filter(is_active=True)
    return render(request, template_name, {'products':api_obj, 'title': "Cable Tv", 'link': '/customer/recharge/select-cabletv'})

@login_required(login_url=settings.LOGIN_URL)
def selectBillAndPackage(request, code):
	template_name = 'cables/customer_check_api.html'
	obj = CableRecharegAPI.objects.filter(is_active=True, identifier=code)
	toJson=""
	items = []
	if len(obj) > 0:
		toJson = json.loads(obj[0].cable_type_price)
		for i in toJson:
			item = {}
			x = i.split('|')

			if len(x) > 3:
				item['api_code'] = x[0]
				item['what_user_sees'] = x[1]
				item['api_price'] = x[2]
				item['site_price'] = x[3]
				try:
					item['site_service_code'] = x[4]
				except:
					pass
				items.append(item)
			else:
				pass
		return render(request, template_name, {'code': code , 'obj': obj[0], 'items': items})
	messages.error(request, "Something is WRONG, contact the admin for resolution")
	return render(request, template_name, {'code': code , 'obj': obj, 'items': items})

@login_required(login_url=settings.LOGIN_URL)
def Check_Customer(request):
    code = "" 
    if request.method == 'POST':
        smart_no = request.POST['smart_no']
        service = request.POST['cable_bill']
        product_code = request.POST['product_code']
        code = product_code.split('|')[0]
        site_service_code = product_code.split('|')[1]
        getActiveApi = CableRecharegAPI.objects.filter(is_active=True, identifier=code)
        print(getActiveApi)
        if len(getActiveApi) < 1:
            messages.info(request, "No API activated for this service")
            return redirect('selectBillAndPackage', code=code.strip())
        service_code = json.loads(getActiveApi[0].cable_type_price)

        d_code = [sc for sc in service_code if site_service_code in sc]
        d__code = d_code[0].split("|")

        eurl = getActiveApi[0].customerCheck
        url = eurl.replace('[SMART_NO]', smart_no)
        url = url.replace('[SERVICE]', service)
        r = requests.get(url)
        info = (r.content).decode("utf-8")
        resp = json.loads(info)
        if resp:
            print(resp)
            print(code, "pppppppp")
            context = {
                'resp': resp,
                'smart_no':smart_no,
                'service':service,
                'amount':d__code[2],
                'amount_to_deduct': d__code[3],
                'ref':service[0] + service[1] + service[2]  + get_random_string(length=10),
                'service_code': site_service_code,
                'product_code': product_code,
            }
        return render(request, 'cables/process_subscription.html', context)
    return redirect(reverse("rechargeapp:cabletvtemplate"))

def getPlanCodeVsUrlVariable(value):
    x = value.split('%')
    try:
        return [x[0], x[1]]
    except (ValueError, IndexError):
        return [x[0], 'no url variable'] 
    
@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@transaction.atomic
def SubscribeCable(request):
	from transactions.models import Transactions
	try:
		user = request.user
		print(request.POST)
		code = ""
		if request.method == 'POST':
			smart_no = (request.POST['smart_no']).strip()
			service_code = request.POST['service_code']
			service = request.POST['service']
			customer_number = request.POST.get('customer_number', 'no number')
			customer_name = request.POST['customer_name']
			plan__code = request.POST['product_code'].split('|')
			plan_code = plan__code[1]
			code = plan__code[0]
			plan_amount = request.POST['amount']
			amount = request.POST['amount_to_deduct']
			ordernumber = request.POST['ref']
			invoice = request.POST.get('invoice', 'default')
			phone = user.userprofile.phone if not request.POST['phone'] else request.POST['phone']
			# if prevent_double.prevent_doubles(request, code, smart_no):
			# 	messages.error(request, 'Transaction error this seems to be a duplicate request else retry in a minute')
			# 	return redirect(reverse('rechargeapp:cabletvtemplate'))

			getActiveApi = get_or_none(CableRecharegAPI, is_active=True, identifier=code)

			smsbal = SmsangoSBulkCredit.objects.get(user=user)
			old_balance = smsbal.smscredit
			bonuscre = BonusAccount.objects.get(user=user)

			#Check if to used dasboard credit and if the smscredit is enough to buy the recharge card

			amount = abs(int(amount))
			if float(amount) > float(user.smsbulkcredit.smscredit) or user.smsbulkcredit.smscredit < 0 or float(amount) <= 0:
				messages.error(request, "Insufficient funds")
				return redirect(reverse('rechargeapp:cabletvtemplate'))

			compare = float(int(amount)) <= smsbal.smscredit
			if compare is False:
				messages.error(request, 'Insufficient Balance')
				return redirect(reverse('rechargeapp:cabletvtemplate'))

			from resellers.utility import ProcessUserReseller
			is_reseller = ProcessUserReseller(user, amount, 'cable_tv', service, plan_code)
			if is_reseller[1] is True:
				amount = is_reseller[0]

			smsbal.smscredit -= Decimal(float(amount))
			smsbal.save()

			Transactions.objects.create(
		        user = user,
		        bill_type = "CABLE",
		        bill_code = f"{service_code}|{service}|{plan_code}|{plan_amount}",
		        bill_number = smart_no,
		        identifier = code,
		        actual_amount = amount,
		        paid_amount = amount,
		        old_balance = old_balance,
		        new_balance = smsbal.smscredit,
		        status = "QUEUE",
		        api_id = getActiveApi.id,
		        mode = "DIRECT",
		        phone = phone,
		        customernumber = customer_number,
		        customername = customer_name,
		        reference = timezoneshit()
		    )
			print("ssdfgsfgsdgfsgjgsgfsgfgh")

			messages.success(request, "Request has been submitted")
			return redirect("rechargeapp:cabletvtemplate")
		else:
			return redirect(reverse('rechargeapp:cabletvtemplate'))
	except Exception as e:
		print(e)
		return redirect("rechargeapp:cabletvtemplate")
	# return redirect(reverse("rechargeapp:cabletv", kwargs={'code':code.strip()}))

@transaction.atomic
def ProcessCablePurchase(object_id):
	from transactions.models import Transactions
	t = Transactions.objects.get(pk=object_id, status="QUEUE")
	# t.status = "PROCESSING"
	# t.save()
	user = t.user
	getActiveApi = get_or_none(CableRecharegAPI, is_active=True, pk=t.api_id)
	ordernumber = t.reference
	[service_code, service, plan_code, plan_amount] = t.bill_code.split("|")
	amount = t.actual_amount
	amount_c = t.actual_amount
	t.reference = ordernumber
	if getActiveApi is None:
		t.comment = "api not activated, contact the admin"
		t.save()
		return ""

	ap_plan = {}
	for x in json.loads(getActiveApi.cable_type_price):
		if plan_code in x.split("|"):
			# ap_plan.append(x.split("|")[0])
			ap_plan["api_code"] = x.split("|")[0]
			try:
				ap_plan["amount"] = x.split("|")[4]
			except:
				pass
	api_code = ap_plan["api_code"]


	smsbal = user.smsbulkcredit
	print(int(smsbal.smscredit), int(t.old_balance), "---------")

	if int(smsbal.smscredit) != int(t.new_balance) and t.mode != "API":
		t.comment = "Fraud Detected"
		t.status = "FAILED"
		t.save()
		return "Done"
		
	else:
		eurl = getActiveApi.api_url
		url_data = getActiveApi.api_url_data
		replaceables = ['[SMART_NO]', '[SERVICE]','[SERVICE_CODE]','[CUSTOMER_NUMBER]', '[CUSTOMER_NAME]', '[PLAN_CODE]', '[PLAN_AMOUNT]', '[PHONE]', '[ORDER_NUMBER]', '[API_CODE]']
		replaceWith = [t.bill_number, service, service_code, t.customernumber, t.customername, plan_code, plan_amount, t.phone, ordernumber, api_code]
		print(replaceWith)
		for i,j in zip(replaceables, replaceWith):
			eurl = eurl.replace(i,str(j))
			url_data = str(url_data).replace(i,str(j))
		print(eurl)
		print(url_data)
		paramet = ast.literal_eval(url_data)

		from resellers.utility import ProcessUserReseller
		is_reseller = ProcessUserReseller(user, float(t.paid_amount), 'cable_tv', getActiveApi.identifier, plan_code)


		from vbp_helper import request_method
		info = request_method.call_external_api(eurl, paramet['data'], paramet['headers'])
		print(info)

		if any(respo in str(info) for respo in getActiveApi.success_code.split(",")):
			
			try:
				infoo = json.loads(info)
				jinfo = evalResponse(infoo)
				jinfo['site_amount'] = amount
				print(jinfo)

				t.status = "SUCCESS"
				t.api_response = json.dumps(jinfo)
				t.save()
			except:
				infoo = info
				jinfo = {}
				jinfo['site_amount'] = amount
				jinfo['result'] = info
				print(jinfo)

				t.status = "SUCCESS"
				t.api_response = json.dumps(jinfo)
				t.save()

			if not is_reseller[1] is True:
				bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
				if not bonus_to_add is None:
					try:
						getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.purchase_bill_bonus) 
						bonuscre.bonus += Decimal(getbonus_amt * float(amount))
						bonuscre.save()
						getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_cable_bonus)
						getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
						CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
					except:
						pass
		else:
			smsbal.smscredit += Decimal(is_reseller[0] if is_reseller[1] else float(amount))
			smsbal.save()

			t.status = "FAILED"
			t.api_response = info
			t.paid_amount = 0.0
			t.new_balance = user.smsbulkcredit.smscredit
			t.save()

			from api_errors.views import ReturnErrorResponse
			resp = ReturnErrorResponse(info, getActiveApi.api_name, "Decoder recharge was not successful")
	if t.callback_url:
		request_method.call_external_api(t.callback_url, {"status": t.status}, {}) 