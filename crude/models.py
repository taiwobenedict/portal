from django.db import models
from transactions.models import Transactions
from django.db.models.signals import pre_save, post_save, post_migrate
from django.dispatch import receiver

from transactions.models import Transactions
from rechargeapp.views import ProcessAirtimePurchase, ProcessDataPurchase
from rechargeapp.cable_view import ProcessCablePurchase
from electricity.views import ProcessElectricityPurchase

@receiver(post_save, sender=Transactions)
def process_order(sender, **kwargs):
	r = kwargs["instance"]
	if r.bill_type == "AIRTIME" and r.status == "QUEUE":
		ProcessAirtimePurchase(r.id)
	elif r.bill_type == "DATA" and r.status == "QUEUE":
		ProcessDataPurchase(r.id)
	elif r.bill_type == "CABLE" and r.status == "QUEUE":
		ProcessCablePurchase(r.id)
	elif r.bill_type == "ELECTRICITY" and r.status == "QUEUE":
		ProcessElectricityPurchase(r.id)
