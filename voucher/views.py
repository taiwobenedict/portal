from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages 
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required

from random import randint
import random, json
from voucher.models import GeneratedVoucher, UsedVouchers
from smsangosend.models import SmsangoSBulkCredit
from coreconfig.models import *
from voucher.utility import get_or_none
from decimal import *
from payments.models import PayStackPayment
from django.conf import settings
from django.db import transaction

def GenerateVoucherFunction(amt, number):
  for i in range(0, int(number)):
    sec,first = randint(2,4), randint(10,15)
    # config = DashboardConfig.objects.all()
    wetin = [get_random_string(length=first), get_random_string(length=sec)]
    voucher = settings.VOUCHER_PREFIX + wetin[0] + wetin[1] + '/'+ (str(int(amt)/100))[0]
    checkIfVoucherExist = get_or_none(GeneratedVoucher, voucher=voucher)
    if checkIfVoucherExist is None:
      GeneratedVoucher.objects.create(
        voucher = voucher,
        voucher_amount = int(amt),
        status = 'UN-USED'
      )
    else:
      number+=number
      pass
  generated = GeneratedVoucher.objects.all().order_by('-date')[:int(number)]
  return generated

@login_required(login_url=settings.LOGIN_URL)
def GenerateVouchersTemplate(request):
  user = request.user
  template_name = 'voucher/generate_vouchers.html'
  if user.is_staff:
    return render(request, template_name)
  else:
    messages.info(request, "You are not authorized access this part")
    return HttpResponseRedirect("/")
  return render(request, template_name)

@login_required(login_url=settings.LOGIN_URL)
def GenerateVouchersV(request):
  user = request.user
  template_name = 'voucher/generate_vouchers.html'
  if user.is_staff:
    numberOfVoucher = request.GET.get('numberOfVoucher')
    amountOfVoucher = request.GET.get('amountOfVoucher')
    generated = GenerateVoucherFunction(amountOfVoucher, numberOfVoucher)
    # generated = [x.voucher for x in generated]
    return render(request, template_name, {'generated':generated})
  else:
    messages.info(request, "You are not authorized access this part")
    return HttpResponseRedirect("/")
  return render(request, template_name)

@login_required(login_url=settings.LOGIN_URL)
def ListVouchers(request):
  template_name='voucher/list_vouchers.html'
  user = request.user
  if user.is_staff:
    try:
      getVouchers = ""
      vouchersToGet = request.GET['voucherType']
      if vouchersToGet == 'unused':
        getVouchers = GeneratedVoucher.objects.filter(status='UN-USED')
      elif vouchersToGet == 'used':
        getVouchers = GeneratedVoucher.objects.filter(status='USED')
      elif vouchersToGet == 'all':
        getVouchers = GeneratedVoucher.objects.all()
      return render(request, template_name, {'getVouchers':getVouchers})
    except Exception as e:
      # raise e
      getVouchers = GeneratedVoucher.objects.all()
      return render(request, template_name, {'getVouchers':getVouchers})
  return render(request, template_name, {})

@login_required(login_url=settings.LOGIN_URL)
@transaction.atomic
def LoadVoucher(request):
  template_name = "voucher/load_vouchers.html"
  user = request.user
  smsbal = SmsangoSBulkCredit.objects.get(user=user)
  old_balance = smsbal.smscredit
  if request.method == "POST":
    voucherCode = request.POST['voucherCode']
    bringVoucherInstance = get_or_none(GeneratedVoucher, voucher=voucherCode.strip())
    if bringVoucherInstance is not None:
      checkifVwasUsed = get_or_none(UsedVouchers, voucher=bringVoucherInstance)
      if checkifVwasUsed is None:
        smsbal.smscredit += Decimal(int(bringVoucherInstance.voucher_amount))
        smsbal.save()
        getVoucher = GeneratedVoucher.objects.get(voucher=voucherCode.strip())
        getVoucher.status = 'USED'
        getVoucher.save()
        usedvouchers = UsedVouchers.objects.create(
          voucher=getVoucher, 
          user=user,
          status='USED'
        )
        obj = PayStackPayment.objects.create(
          user = user,
          smsangosbulkcredit = smsbal,
          order_id = voucherCode,
          old_balance = float(old_balance),
          new_balance = float(smsbal.smscredit),
          amtcredited = Decimal(int(bringVoucherInstance.voucher_amount)),
          amount = int(bringVoucherInstance.voucher_amount),
          reference = voucherCode,
        )
        messages.success(request, voucherCode +' Voucher loaded successfully' + str(bringVoucherInstance.voucher_amount))
        return HttpResponseRedirect(reverse('voucher:loadVoucher'))
      else:
        messages.warning(request, 'Dont do that, Voucher has been previously used')
        return HttpResponseRedirect(reverse('voucher:loadVoucher'))
      return HttpResponseRedirect(reverse('voucher:loadVoucher'))
    messages.warning(request, "voucher exists not")
    return HttpResponseRedirect(reverse('voucher:loadVoucher'))
  else:
    return render(request, template_name, {})

@login_required(login_url=settings.LOGIN_URL)
def UserUsedVouchers(request):
  template_name='voucher/list_vouchers.html'
  user = request.user
  vouchersToGet = request.query_params['voucherType']
  getVouchers = UsedVouchers.objects.all(user=user)
  return render(request, template_name, {'getVouchers':getVouchers})

