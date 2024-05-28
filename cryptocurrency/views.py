from django.shortcuts import render, redirect
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from electricity.models import *
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge
from smsangonumcredit.models import BonusesPercentage
from rechargeapp.models import BonusAccount
from api.views import QueryStringBasedTokenAuthentication, getApiKey
from rechargeapp.utility import get_or_none
import requests
import json
from decimal import Decimal
from cryptocurrency.models import *
from cryptocurrency.serializer import CryptoCurrenciesSerializer 
from vbp_helper.helpers import evalResponse
from django.conf import settings


""" Template the render the crypro currency"""
@login_required(login_url=settings.LOGIN_URL)
def cryptoCurrencyTemplate(request):
  user = request.user
  getCryptoApi = get_or_none(CryptoCurrencyAPI, is_active=True)
  if getCryptoApi != None:
    context = {
      'crypto_currencies': json.loads(getCryptoApi.currencies_trading)
    }
    return render(request, 'cryptocurrency/cryptoPurchase.html', context)
  return render(request, 'cryptocurrency/cryptoPurchase.html', { 'crypto_currencies': "NO API WAS ACTIVATED"})

@login_required(login_url=settings.LOGIN_URL)
def cryptoPurchase(request):
  user = request.user
  if request.method == 'POST':
    currency = request.POST['currency']
    amount = request.POST['amount']
    trans_id = 'CRYPTO' + get_random_string(length=9)

    getCryptoApi = get_or_none(CryptoCurrencyAPI, is_active=True)

    url = (getCryptoApi.api_url).strip()
    replace_keys = (('[CRYPTO_CURRENCY]',currency),('[TRANSACTION_ID]',trans_id))
    for (i,j) in replace_keys:
      url = url.replace(i,j)
    print(url)
    CryptoCurrencies.objects.create(
      user = user,
      currency=currency,
      amount=amount,
      trans_id=trans_id,
      status="PENDING"
    )
    return redirect(url)
  else:
    messages.error(request, 'Error Ordering Crypto Currency')
    return redirect('cryptocurrency:cryptoTemplate')

@login_required(login_url=settings.LOGIN_URL)
def cryptoTransactions(request):
  user = request.user
  transac = CryptoCurrencies.objects.filter(user=user).order_by('-date')
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
  return render(request, 'cryptocurrency/cryptoHistory.html', {'historys': transac, })
