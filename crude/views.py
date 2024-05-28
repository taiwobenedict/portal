from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rechargeapp.models import RechargeAirtimeAPI, CableRecharegAPI, DataNetworks
from electricity.models import ElectricityApis
from smsangosend.models import APIUrl
from smsangosend.models import SmsangoSendSMS
import json

@login_required(login_url=settings.LOGIN_URL)
def load_configurations(request):
	load_data = request.GET.get("config")
	data = None
	try:
	    f = open(f"crude/{load_data}_config.json")
	    data = json.load(f)
	    f.close()
	    if request.user.is_superuser and data:
	    	if load_data == "airtime":
	    		for item in data:
	    			RechargeAirtimeAPI.objects.create(
						api_name = item['api_name'],
						is_active = False,
						api_url = item['api_url'],
						api_url_data = item['api_url_data'],
						api_url_balance = "None",
						identifier=item['identifier'],
						network_image = item['network_image'],
						user_discount = item['user_discount'],
						success_code = item['success_code'],
						description = item['description'],
					)
	    	elif load_data == "data":
	    		for item in data:
	    			DataNetworks.objects.create(
						api_name = item['api_name'],
						is_active = False,
						api_url = item['api_url'],
						api_url_data = item['api_url_data'],
						api_url_balance = "None",
						identifier=item['identifier'],
						network_image = item['network_image'],
						network_data_amount_json = item['network_data_amount_json'],
						success_code = item['success_code'],
						description = item['description'],
					)
	    	elif load_data == "electricity":
	    		for item in data:
	    			ElectricityApis.objects.create(
						api_name = item['api_name'],
						is_active = False,
						api_url = item['api_url'],
						api_url_data = item['api_url_data'],
						api_url_balance = "None",
						api_url_check = item['api_url_check'],
						identifier=item['identifier'],
						electricity_image = item['electricity_image'],
						electricity_code_json = item['electricity_code_json'],
						metertype_code_json = item['metertype_code_json'],
						success_code = item['success_code'],
						check_success_code = item['check_success_code'],
						res_params = item['res_params'],
						commission = item['commission'],
						description = item['description'],
					)
	    	elif load_data == "cable":
	    		print("cable", data)
	    		for item in data:
	    			CableRecharegAPI.objects.create(
						api_name = item['api_name'],
						is_active = False,
						api_url = item['api_url'],
						api_url_data = item['api_url_data'],
						api_url_balance = "None",
						identifier=item['identifier'],
						cable_image = item['cable_image'],
						customerCheck = item['customerCheck'],
						cable_type_price = item['cable_type_price'],
						success_code = item['success_code'],
						successCheckCode = item['successCheckCode'],
						res_params = item['res_params'],
						description = item['description'],
					)
	    	elif load_data == "bulksms":
	    		for item in data:
	    			APIUrl.objects.create(
						api_name = item['api_name'],
						is_active = False,
						apurl = item['apurl'],
						apurl_data = item['apurl_data'],
						apiamtpersms=item['apiamtpersms'],
						api_response = item['api_response']
					)
	    	elif not load_data:
	    		messages.error(request, f"Error occurred while loading configurations")
	    		return render(request, "admin/pre_load_config.html")
	    	messages.success(request, f"{load_data.upper() if load_data else ''} configurations has been successfully loaded")
	    	return redirect("load_config")
	except Exception as e:
		if load_data == None:
			return render(request, "admin/pre_load_config.html")
		messages.error(request, str(e))
		return render(request, "admin/pre_load_config.html")
