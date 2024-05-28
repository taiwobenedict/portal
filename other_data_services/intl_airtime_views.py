import ast
from other_data_services.imports import *
from other_data_services.serializer import IntAirtimeTransactionsSerializer
from vbp_helper.helpers import timezoneshit

# now = datetime.now()
# stamp = mktime(now.timetuple())
# print format_date_time(stamp) 

""" Int Logic """
@login_required(login_url=settings.LOGIN_URL)
def intAirtimeView(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')

  template_name="intl_airtime.html"
  return render(request, template_name, {"commission": IntAirtimeApi.objects.filter(is_active=True).first()})

class CheckIntNumber(APIView):
  # ["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      number = params['number']
      getActiveApi = IntAirtimeApi.objects.get(is_active=True)
      url = (getActiveApi.check_api_url).strip()
      url_data = (getActiveApi.check_url_data).strip()
      url = url.replace('[NUMBER]',number)
      url_data = url_data.replace('[NUMBER]',number)
      paramet = json.loads(url_data)
      r = requests.post(url, data=paramet['data'], headers=paramet['headers'])
      info = (r.content).decode("utf-8")
      print(url, paramet)
      print(info)
      if getActiveApi.success_check_code in str(info):
        return Response({"status":200, "message": "success", "details": json.loads(info)}, status=200)
      else:
        return Response({"status":400, "message": "Error", "details": info}, status=400)
    except Exception as e:
      raise e
      return Response({"status":400, "message": "Error", "details":"Bad Request"})

class PurchaseIntAirtime(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      params = request.query_params
      user = request.user
      ordernumber = timezoneshit()
      product_id, number, amount, country, country_code, network, currency, rate, operator, variation_code =  \
        params['product_id'], params['number'], params['amount'],\
          params['country'], params['country_code'], params['network'], params['currency'], params['rate'], params["operator"], params["variation_code"]
      getActiveApi = IntAirtimeApi.objects.get(is_active=True)
      smsbal = SmsangoSBulkCredit.objects.get(user=user)
      old_balance = smsbal.smscredit
      bonuscre = BonusAccount.objects.get(user=user)
      amt = abs((float(rate) * float(amount))+ getActiveApi.commission)
      compare = amt <= smsbal.smscredit
      if compare is True:

        from resellers.utility import ProcessUserReseller
        is_reseller = ProcessUserReseller(user, rate, 'int_airtime', 'int_airtime')
        if is_reseller[1] is True:
          rate = is_reseller[0]

        smsbal.smscredit -= Decimal(amt)
        smsbal.save()
        obj = IntAirtimeTransactions.objects.create(
          user = user,
          trans_id = ordernumber,
          amount = float(amt),
          api_code = product_id,
          numberRecharged = number,
          network_recharged = network,
          # currency = currency,
          country = country,
          resp = "No response yet",
          status = "Pending",
          old_balance = float(old_balance),
          new_balance = float(smsbal.smscredit)
        )

        url = (getActiveApi.api_url).strip()
        url_data = str(getActiveApi.api_url_data)
        replace_keys = (('[PRODUCT_ID]',product_id),('[NUMBER]',number),('[AMOUNT]',amount), ('[ORDERNUMBER]', ordernumber), ('[COUNTRY]', country), ('[COUNTRY_CODE]', country_code), ('[OPERATOR]', operator), ('[VARIATION]', variation_code), ('[CURRENCY]', currency))
        for (i,j) in replace_keys:
          url = url.replace(i,j)
          url_data = url_data.replace(i,j)
        paramet = ast.literal_eval(url_data)
        from vbp_helper import request_method
        info = request_method.call_external_api(url, paramet['data'], paramet['headers'])
        print(info)
        if any(respo in str(info) for respo in getActiveApi.success_code.split(",")):

          obj.resp = info,
          obj.status = "SUCCESS"
          obj.save()

          if is_reseller[1] is True:
            pass
          else:
            bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
            if bonus_to_add is None:
              pass
            else:
              getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.spectranet_bonus)
              bonuscre.bonus += Decimal(getbonus_amt * float(amount))
              bonuscre.save()
              getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_spectranet_bonus)
              getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
              CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
          return Response({"status":201, "message": "success", "details":"Recharge successful"})
        else:
          smsbal.smscredit += Decimal(amt)
          smsbal.save()

          obj.resp = info
          obj.status = "FAILED"
          obj.old_balance = float(old_balance)
          obj.new_balance = float(smsbal.smscredit)
          obj.save()

        return Response({"status":400, "message": "Error", "details":"Not Successful"})
      else:
        return Response({"status":405, "message": "Error", "details":"Insufficient Balance"})
    except Exception as e:
      raise e
      return Response({"status":403, "message": "Error", "details":"Bad Request"})

class IntAirtimeDTransactions(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      user = getUser.user
      transac = IntAirtimeTransactions.objects.filter(user=user).order_by('-date')
      transac = IntAirtimeTransactionsSerializer(transac, many=True)
      if not transac.data:
        return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
      return Response({'status':200, 'message':'Int Airtime transaction retrieve successfully', 'details': transac.data})
    except Exception as e:
      return Response({'status':400, 'message':'Bad Request'})

@login_required(login_url=settings.LOGIN_URL)
def IntAirtimeDTransaction(request):
    user = request.user
    template_name='intl_airtime_history.html'
    transac = IntAirtimeTransactions.objects.filter(user=user).order_by('-date')
    paginator = Paginator(transac, 10)#show 20 per page
    page = request.GET.get('page')
    try:
      historys = paginator.page(page)
    except PageNotAnInteger:
      # If page is not an integer, deliver first page.
      historys = paginator.page(1)
    except EmptyPage:
      # If page is out of range (e.g. 9999), deliver last page of results.
      historys = paginator.page(paginator.num_pages)
    return render(request, template_name, {'historys': transac})
