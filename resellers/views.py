from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages 
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required

from random import randint
import random
from resellers.models import *
from smsangosend.models import SmsangoSBulkCredit
from smsangonumcredit.models import BonusesPercentage
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge
from coreconfig.models import *
from resellers.utility import get_or_none
from decimal import *
from payments.models import PayStackPayment
from django.conf import settings
from django.db import transaction

@login_required(login_url=settings.LOGIN_URL)
@transaction.atomic
def ResellerActivation(request):
  template_name = 'resellers/activate_reseller.html'
  user = request.user
  obj = ResellerLevelsAndPercentage.objects.filter(is_active=True)

  if request.method == 'POST':
    reseller_level = request.POST['reseller_level']

    reseller_percent_obj = obj.get(name=reseller_level)
    amount = reseller_percent_obj.cost_of_activation

    smsbal = SmsangoSBulkCredit.objects.get(user=user)
    old_balance = smsbal.smscredit
    compare = float(int(amount)) <= smsbal.smscredit

    if compare is True:
      smsbal.smscredit -= Decimal(amount)
      smsbal.save()
      ResellerStatus.objects.get_or_create(
        user=user,
        is_reseller=True,
        reseller_level=reseller_level
      )
      ResellerHistory.objects.create(
        user=user,
        amount=amount,
        old_balance=old_balance,
        new_balance=smsbal.smscredit,
        previous_reseller_level="Ordinary User",
        reseller_level=reseller_level,
        action="Activated"
      )
      bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
      if bonus_to_add is None:
        pass
      else:
        try:
            getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_activation_reseller_bonus)
            getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
            CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
        except Exception as e:
            pass
      messages.success(request, 'You are now a {} reseller'.format(reseller_level))
      return redirect('resellers:upgrade')
    else:
      messages.error(request, 'Insufficient Funds')
      return redirect('resellers:activate')
  return render(request, template_name, {'action':'activation','obj2':obj, 'obj': obj.order_by('cost_of_activation')})

@login_required(login_url=settings.LOGIN_URL)
@transaction.atomic
def ResellerUpgrade(request):
  template_name = 'resellers/activate_reseller.html'
  user = request.user
  obj = ResellerLevelsAndPercentage.objects.filter(is_active=True)
  get_reseller = ResellerStatus.objects.get(user=user)
  #GET USER RESELLER LEVEL DETAILS
  current_reseller_pkg = obj.get(name=get_reseller.reseller_level)
  if request.method == 'POST':
    reseller_level = request.POST['reseller_level']

    #GET NEW RESELLER PACKAGE LEVEL DETAILS
    reseller_pkg_obj = obj.get(name=reseller_level)
    amount = reseller_pkg_obj.cost_of_activation

    #COMPARE THE TWO PACKAGES
    if current_reseller_pkg.cost_of_activation >= amount:
      messages.error(request, 'You can only upgrade to higher package')
      return redirect('resellers:upgrade')
    reseller_pkg_diff = amount - current_reseller_pkg.cost_of_activation

    smsbal = SmsangoSBulkCredit.objects.get(user=user)
    old_balance = smsbal.smscredit
    compare = float(int(reseller_pkg_diff)) <= smsbal.smscredit

    if compare is True:
      smsbal.smscredit -= Decimal(reseller_pkg_diff)
      smsbal.save()

      get_reseller.reseller_level = reseller_level
      get_reseller.save()

      ResellerHistory.objects.create(
        user=user,
        amount=amount,
        old_balance=old_balance,
        new_balance=smsbal.smscredit,
        previous_reseller_level=current_reseller_pkg.name,
        reseller_level=reseller_level,
        action="Upgrade"
      )
      bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
      if bonus_to_add is None:
        pass
      else:
        try:
          getrefbonus_percent = 0 if bonus_to_add is None else float(bonus_to_add.referral_upgrade_reseller_bonus)
          getrefbonus_amt = Decimal(getrefbonus_percent * float(amount))
          CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
        except Exception as e:
          pass
      messages.success(request, 'You are now a {} reseller'.format(reseller_level))
      return redirect('resellers:upgrade')
    else:
      messages.error(request, 'You dont have enough funds in your wallet')
      return redirect('resellers:upgrade')
  print(get_reseller.is_reseller)
  return render(request, template_name, {'action':'upgrading', 'obj2':obj, 'obj': obj.exclude(cost_of_activation__lte=current_reseller_pkg.cost_of_activation).order_by('cost_of_activation')})

@login_required(login_url=settings.LOGIN_URL)
def ResellerHistoryView(request):
  template_name='resellers/reseller_history.html'
  if not request.user.is_superuser:
    return render(request, template_name, {'historys':ResellerHistory.objects.filter(user=request.user)})
  return render(request, template_name, {'historys':ResellerHistory.objects.all()})  

