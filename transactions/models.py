from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
from smsangosend.models import SmsangoSBulkCredit
from django.utils import timezone
import random, time
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

CHOICES = (
	("QUEUE", "QUEUE"),
    ("FAILED", "FAILED"),
    ("REFUNDED", "REFUNDED"),
	("SUCCESS", "SUCCESS"),
)

class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_transactions")
    status = models.CharField(max_length=50, blank=True, null=True)
    identifier = models.CharField(default="", max_length=50)
    bill_type = models.CharField(max_length=500, blank=True, null=True)
    bill_code = models.CharField(max_length=500, blank=True, null=True)
    bill_number = models.CharField(max_length=300, blank=True, null=True)
    bill_serial = models.CharField(max_length=500, blank=True, null=True)
    actual_amount = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    comment = models.CharField(max_length=500, blank=True, null=True)
    reference = models.CharField(max_length=300, blank=True, null=True)
    customernumber = models.CharField(default='', max_length=30, blank=True, null=True)
    customername = models.CharField(default='', max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    customer_dt_number = models.CharField(max_length=100, default='', blank=True, null=True)

    #insurance
    insured_name = models.CharField(max_length=300, default='', blank=True, null=True)
    engine_number = models.CharField(max_length=100, default='', blank=True, null=True)
    chasis_number = models.CharField(max_length=300, default='', blank=True, null=True)
    plate_number = models.CharField(max_length=300, default='', blank=True, null=True)
    vehicle_make = models.CharField(max_length=300, default='', blank=True, null=True)
    vehicle_color = models.CharField(max_length=100, default='', blank=True, null=True)
    vehicle_model = models.CharField(max_length=100, default='', blank=True, null=True)
    year_of_make = models.CharField(max_length=100, default='', blank=True, null=True)
    contact_address = models.CharField(max_length=300, default='', blank=True, null=True)
    date_of_birth = models.CharField(max_length=300, default='', blank=True, null=True)
    next_of_kin_name = models.CharField(max_length=300, default='', blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=300, default='', blank=True, null=True)
    photo = models.TextField(max_length=100000, default='', blank=True, null=True)
    extra_info = models.CharField(max_length=300, default='', blank=True, null=True)
    business_occupation = models.CharField(max_length=300, default='', blank=True, null=True)
    type_building = models.CharField(max_length=300, default='', blank=True, null=True)
    business_occupation = models.CharField(max_length=300, default='', blank=True, null=True)
    #end insurance

    api_id = models.IntegerField(blank=True, null=True)

    #for account funding
    smsangosbulkcredit = models.ForeignKey(SmsangoSBulkCredit, on_delete=models.CASCADE, related_name="wallet_funding", null=True, blank=True)
    amtcredited = models.FloatField(blank=True, null=True)
    #end for account funding
    
    api_response = models.TextField(max_length=20000, blank=True, null=True)
    callback_url = models.TextField(max_length=20000, blank=True, null=True)
    callback_done = models.BooleanField(default=False)
    mode = models.CharField(max_length=200, default="DIRECT")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     getLastOne = Transactions.objects.all()
    #     if getLastOne.count() == 0:
    #         super(Transactions, self).save(*args, **kwargs)
    #     else:

    #         getLastOne = getLastOne.last()

    #         # if (int(timezone.now().timestamp()) - int(getLastOne.created_at.timestamp()) <= 2) and (getLastOne.user == self.user) and (self.bill_number == getLastOne.bill_number) and getLastOne.status == "QUEUE":
    #         #     raise ValidationError("Denied by fraud detection")
    #         #     return ""
    #         super(Transactions, self).save(*args, **kwargs)
    #         # else:
    #         #     super(Transactions, self).save(*args, **kwargs)

@receiver(pre_save, sender=Transactions)
def transaction_pre_save_receiver(sender, **kwargs):
    instance = kwargs['instance']
    print(instance, kwargs)
    if instance and not kwargs['update_fields']:
        try:
            t = Transactions.objects.all()
            if t.count() > 0:
                getLastOne = t.last()
                print(int(timezone.now().timestamp()) - int(getLastOne.created_at.timestamp()), "sept")
                if (int(timezone.now().timestamp()) - int(getLastOne.created_at.timestamp()) <= 5) \
                and (getLastOne.user == instance.user) and (instance.bill_number == getLastOne.bill_number) and\
                 instance.status == "QUEUE" and instance.mode != "API":
                    raise ValidationError("Denied by fraud detection")
                else:
                    pass
            else:
                pass
                
        except Exception as e:
            raise e
    else:
        pass