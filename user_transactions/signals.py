from payments.models import PayStackPayment
from rechargeapp.models import AirtimeTopup, MtnDataShare, CableRecharge
from electricity.models import Electricity
from education.models import ResultCheckers
from insurance.models import HealthInsuranceHistory, PersonalInsuranceHistory, HomeCoverInsuranceHistory, InsuranceHistory
from transferApp.models import TransferDetailsHistory
from user_to_user_transfer.models import UserToUserTransferHistory
from universal_rcp.models import UniversalCardPrinting
from recharge_printing.models import CardPrinting
from resellers.models import ResellerHistory
from smsangosend.models import SmsangoSBulkCredit
from other_data_services.models import SmileTransactions, SpectranetTransactions
from django.contrib.auth.models import User


from user_transactions.models import AllUserTransactionsLogs

from django.db.models.signals import pre_init, pre_save, post_save
from django.dispatch import receiver

record_id = []

@receiver(pre_init, sender=SmsangoSBulkCredit)
def monitor_da(sender, *arg, **kwargs):
  print("executed first")
  print(kwargs)
  print(kwargs['args'][2])
  user_obj = User.objects.get(id=kwargs['args'][1])
  record = AllUserTransactionsLogs.objects.create(user=user_obj, old_balance=kwargs['args'][2])
  record_id.append(record.id)


@receiver(post_save, sender=SmsangoSBulkCredit)
def see_new(sender, instance, created, **kwargs):
  if not created:
    print('not created')
    print(record_id, "record id")
    obj = AllUserTransactionsLogs.objects.get(id=record_id[0])
    print(obj, "-------")
    obj.service = 'test'
    obj.new_balance = instance.smscredit
  else:
    print('created')