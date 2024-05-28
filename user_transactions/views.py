from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from payments.models import PayStackPayment
from rechargeapp.models import AirtimeTopup, MtnDataShare, CableRecharge
from electricity.models import Electricity
from education.models import ResultCheckers
# from insurance.models import HealthInsuranceHistory, PersonalInsuranceHistory, HomeCoverInsuranceHistory, InsuranceHistory
# from transferApp.models import TransferDetailsHistory
#from user_to_user_transfer.models import UserToUserTransferHistory
# from universal_rcp.models import UniversalCardPrinting
# from recharge_printing.models import CardPrinting
from resellers.models import ResellerHistory
from smsangosend.models import SmsangoSBulkCredit
from other_data_services.models import SmileTransactions, SpectranetTransactions
from django.contrib.auth.models import User
from django.db.models import Q, Sum

from django.shortcuts import render, redirect, HttpResponse

from user_transactions.models import AllUserTransactionsLogs
import datetime
from decimal import Decimal

#LogTransactionIntoTransactions(request=REQUEST, log=None, old_balance=nONE, new_balance=NOEE, service=KSKD, trans_id=None, amount=None)
def LogTransactionIntoTransactions(**kwargs):
  obj = AllUserTransactionsLogs.objects.create(
    user= kwargs['request']['user'],
    service=kwargs['service'],
    old_balance=kwargs['old_balance'],
    new_balance=kwargs['new_balance'],
    amount=kwargs['amount'],
    trans_id=kwargs['trans_id'],
    log=kwargs['log']
  )
  return obj

@login_required(login_url='/customer/login')
def listUserTranasactions(request):
  from transactions.models import Transactions
  template_name = "user_transactions/user_transactions.html"
  if request.user.is_staff is True or request.user.is_superuser is True:
    transac = Transactions.objects.all().order_by('-created_at')
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
    return render(request, template_name, {'historys': transac, })
  else:
    return HttpResponse("/")

@login_required(login_url='/customer/login')
def transaction_statistics(request):
  from transactions.models import Transactions
  template_name = "user_transactions/user_statistics.html"
  if request.user.is_staff is True or request.user.is_superuser is True:
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    date_chk = start_date is None or end_date is None
    print(date_chk)
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date() if not date_chk else start_date
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date() if not date_chk else end_date

    print(start_date, end_date)

    airtime = Transactions.objects.filter(status="SUCCESS", bill_type="AIRTIME").count() if date_chk else Transactions.objects.filter(status="SUCCESS", bill_type="AIRTIME", created_at__range=[start_date, end_date]).count()
    data_topup = Transactions.objects.filter(status="SUCCESS", bill_type="DATA").count() if date_chk else Transactions.objects.filter(status="SUCCESS", bill_type="DATA", created_at__range=[start_date, end_date]).count()
    cable_tv = Transactions.objects.filter(status="SUCCESS", bill_type="CABLE").count() if date_chk else Transactions.objects.filter(status="SUCCESS", bill_type="CABLE",created_at__range=[start_date, end_date]).count()
    electricity = Transactions.objects.filter(status="SUCCESS", bill_type="ELECTRICITY").count() if date_chk else Transactions.objects.filter(status="SUCCESS", bill_type="ELECTRICITY", created_at__range=[start_date, end_date]).count()
    result_checkers = ResultCheckers.objects.filter(status="SUCCESS").count() if date_chk else ResultCheckers.objects.filter(status="SUCCESS", date__range=[start_date, end_date]).count()
    wallet = SmsangoSBulkCredit.objects.aggregate(Sum('smscredit'))['smscredit__sum']

    return render(request, template_name, {
      'wallet': wallet,
      'airtime': airtime,
      'data_topup': data_topup,
      'cable_tv': cable_tv,
      'electricity': electricity,
      'result_checkers': result_checkers
    })
  else:
    return HttpResponse("/") 

@login_required(login_url='/customer/login')
def all_transactions(request):
  from transactions.models import Transactions
  template_name = "user_transactions/user_transactions_refunds.html"
  if request.user.is_staff is True or request.user.is_superuser is True:    
    service = request.GET.get('type')
    print(service, "service??????")

    historys = []
    if service is not None:
      historys = Transactions.objects.filter(bill_type=service.upper())
      print(historys, "historys?????")

    return render(request, template_name, {
      'historys': historys,
      'gen_obj': "transactions" if service in ["airtime", "data", "cable", "electricity"] is not None else ""
      # 'data_topup': data_topup,
      # 'cable_tv': cable_tv,
      # 'electricity': electricity,
      # 'result_checkers': result_checkers
    })
  else:
    return HttpResponse("/") 

@login_required(login_url='/customer/login')
def refund_transaction(request):
  from transactions.models import Transactions
  if request.user.is_staff is True or request.user.is_superuser is True:    
    type = request.GET.get('type')
    order_id = request.GET.get('order_id')

    # print(type, order_id)

    try:
      obj = Transactions.objects.get(reference=order_id)
      # print(obj)

      if obj.status == "FAILED":
        obj.status = "REFUNDED"
        obj.old_balance = obj.user.smsbulkcredit.smscredit
        obj.save()

        sms_credit = SmsangoSBulkCredit.objects.get(user=obj.user)
        sms_credit.smscredit += Decimal(obj.paid_amount)
        obj.new_balance = sms_credit.smscredit
        obj.save()
        sms_credit.save()
      else:
        pass
      return redirect("transactions:list_tranasactions")
    except Exception as e:
      raise e
      print(request.path)
      return redirect("transactions:list_tranasactions")
  else:
    return HttpResponse("/") 