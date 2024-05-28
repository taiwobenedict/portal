from other_data_services.imports import *

""" SME Logic """
@login_required(login_url=settings.LOGIN_URL)
def smePage(request):
  user = request.user
  if not user.userprofile.phone:
    messages.success(request, 'Update your profile to proceed')
    return HttpResponseRedirect('/customer/profile-edit')

  getSME = get_or_none(MtnSMEApi, is_active=True)

  smeOptions = ''
  
  if getSME != None:
    smeJson = json.loads(getSME.mtn_sme_code_json)

    smeOptions = [i.split("|")[1] for i in [x for x in smeJson]]

  template_name="mtn_sme.html"
  return render(request, template_name, {"smeOptions":smeOptions})


class PurchaseSme(APIView):
  # ["api_code|what_user_sees|api_price|site_price|product_code|urlvariable|extra_parameter"]
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      if getUser != None:
        user = getUser.user

        phone, what_user_sees = params['phone'], params['smeplan']

        orderNumber = str('SME' + get_random_string(length=9))

        getActiveApi = MtnSMEApi.objects.get(is_active=True)

        service = splitCode(what_user_sees, json.loads(getActiveApi.mtn_sme_code_json))
        api_code, what_user_sees, api_price, amount, product_code, urlvariable, extra_parameter = service[0], service[1], service[2], service[3], service[4], service[5], service[6]

        smsbal = SmsangoSBulkCredit.objects.get(user=user)
        old_balance = smsbal.smscredit
        bonuscre = BonusAccount.objects.get(user=user)
        compare = float(amount) <= smsbal.smscredit
        if compare is True:
          url = (getActiveApi.api_api_url).strip()
          url_data = (getActiveApi.api_url_data).strip()
          replace_keys = (('[PHONE]',phone),('[API_CODE]',api_code),('[API_PRICE]',api_price),('[AMOUNT]',amount),('[ORDERNUMBER]',orderNumber),\
            ('[PRODUCT_CODE]',product_code),('[URLVARIABLE]',urlvariable),('[EXTRA_PARAMETER]',extra_parameter))
          for (i,j) in replace_keys:
            url = url.replace(i,j)
            url_data = url_data.replace(i,j)
          paramet = json.loads(url_data)
          r = requests.post(url, data=paramet['data'], headers=paramet['headers'])
          info = (r.content).decode("utf-8")
          print(info)
          if getActiveApi.success_code in str(info):
            #Process if User is Reseller
            from resellers.utility import ProcessUserReseller
            is_reseller = ProcessUserReseller(user, amount, 'mtn_sme', api_code)
            if is_reseller[1] is True:
              amount = is_reseller[0]

            smsbal.smscredit -= Decimal(amount)
            smsbal.save()
            MtnDataShare.objects.create(
              user = user,
              ordernumber = orderNumber,
              data_amount = float(amount),
              dataSize = what_user_sees,
              data_number = phone,
              data_network = 'MTN SME',
              batchno = orderNumber,
              status = "SUCCESS",
              old_balance = float(old_balance),
              new_balance = float(smsbal.smscredit)
            )
            if is_reseller[1] is True:
              pass
            else:
              bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
              if bonus_to_add is None:
                pass
              else:
                getbonus_amt = 0 if bonus_to_add is None else float(bonus_to_add.mtn_sme_bonus)
                bonuscre.bonus += Decimal(getbonus_amt * float(amount))
                bonuscre.save()
                getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_mtn_sme_bonus)
                getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
                CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
            return Response({"status":201, "message": "success", "details":"Recharge successful"})
          else:
            MtnDataShare.objects.create(
              user = user,
              ordernumber = orderNumber,
              data_amount = float(amount),
              dataSize = what_user_sees,
              data_number = phone,
              data_network = 'MTN SME',
              batchno = orderNumber,
              status = "FAILED",
              old_balance = float(old_balance),
              new_balance = float(smsbal.smscredit)
            )
            return Response({"status":400, "message": "Error", "details":"Not Successful"})
        else:
          return Response({"status":405, "message": "Error", "details":"Insufficient Balance"})
      else:
        return Response({"status":403, "message": "Error", "details":"Not Authorized"})
    except Exception as e:
      raise e
      return Response({"status":403, "message": "Error", "details":"Bad Request"})

# class mtnSMETransactions(APIView):
#   authentication_classes = (QueryStringBasedTokenAuthentication,)
#   permission_classes = (IsAuthenticated,)
#   def get(self, request):
#     try:
#       token = getApiKey(request)
#       getUser = get_or_none(Token, key=token)
#       user = getUser.user
#       transac = SmileTransaction.objects.filter(user=user).order_by('-date')
#       transac = SmileTransactionSerializer(transac, many=True)
#       if not transac.data:
#         return Response({'status':200, 'message':'No Transaction Yet'}, status=200)
#       return Response({'status':200, 'message':'Smile transaction retrieve successfully', 'details': transac.data})
#     except Exception as e:
#       return Response({'status':400, 'message':'Bad Request'})

# @login_required(login_url=settings.LOGIN_URL)
# def SmileTransaction(request):
#     user = request.user
#     template_name='smileHistory.html'
#     transac = SmileTransactions.objects.filter(user=user).order_by('-date')
#     paginator = Paginator(transac, 10)#show 20 per page
#     page = request.GET.get('page')
#     try:
#       historys = paginator.page(page)
#     except PageNotAnInteger:
#       # If page is not an integer, deliver first page.
#       historys = paginator.page(1)
#     except EmptyPage:
#       # If page is out of range (e.g. 9999), deliver last page of results.
#       historys = paginator.page(paginator.num_pages)
#     return render(request, template_name, {'historys': transac, })
