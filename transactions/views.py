from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json

# Create your views here.

from transactions.models import Transactions
from electricity.models import ElectricityApis

@login_required(login_url=settings.LOGIN_URL)
def transactions(request):
	t = []
	if request.user.is_superuser:
		t = Transactions.objects.all().order_by("-id")
	else:
		t = Transactions.objects.filter(user=request.user).order_by("-id")
	template_name = "transactions/index.html"
	return render(request, template_name, {"historys": t})



@login_required(login_url=settings.LOGIN_URL)
def singleOrderApiresponse(request, pk):
	try:
		t = Transactions.objects.get(pk=pk)
		item = {}
		if t.bill_type == "ELECTRICITY":
			api_params = ElectricityApis.objects.get(id=t.api_id)
			api_params = json.loads(api_params.res_params)
			api_response = json.loads(t.api_response)
			for i in api_params:
				try:
					item[i] = api_response[i]
				except:
					pass

			print(item, t.bill_type, api_params, api_response)
			return JsonResponse({"status": "success", "details": item})
		else:
			return JsonResponse({"status": "success", "details": {}})
	except Exception as e:
		raise e
		return JsonResponse({"status": "success", "details": {}})

