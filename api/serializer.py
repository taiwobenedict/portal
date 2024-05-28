from rest_framework import serializers
from rechargeapp.models import (DataNetworks,RechargeAirtimeAPI,AirtimeTopup,CableRecharge,
DataPlansPrices,BonusAccount,RefBonusAccount,MtnDataShare,CableRecharegAPI)
from payments.models import PayStackPayment
from smsangosend.models import UserProfile, SmsangoSendSMS
from notificationapp.models import *
import json
from transactions.models import Transactions
from django.conf import settings
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    exclude = ["password", "last_login"]

class RechargeAirtimeAPISerializer(serializers.ModelSerializer):
  class Meta:
    model = RechargeAirtimeAPI
    fields = ['identifier', 'is_active']

class DataNetworksSerializer(serializers.ModelSerializer):
  class Meta:
    model = DataNetworks
    fields = ['identifier', 'is_active']

class TransactionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transactions
    fields = "__all__"

class AirtimeTopupSerializer(serializers.ModelSerializer):
  class Meta:
    model = AirtimeTopup
    fields = ['id', 'user', 'ordernumber', 'recharge_amount', 'recharge_network', 'recharge_number', 'status', 'purchased_date']

class DataTopupSerializer(serializers.ModelSerializer):
  class Meta:
    model = MtnDataShare
    fields = ['id', 'user', 'ordernumber', 'data_amount', 'data_network', 'data_number','dataSize', 'batchno', 'status', 'purchased_date']

class CableRechargeSerializer(serializers.ModelSerializer):
  class Meta:
    model = CableRecharge
    fields = ['id', 'user', 'ordernumber', 'invoice', 'sub_amount', 'smart_no','billtype', 'customernumber', 'customername', 'phone', 'exchange_reference', 'status','messageresp', 'purchased_date']

class PayStackSerializer(serializers.ModelSerializer):
  class Meta:
    model = PayStackPayment
    fields = ['id', 'user', 'smsangosbulkcredit', 'order_id', 'reference', 'amtcredited', 'amount', 'dated']
#===========================================================31/10/19
class RefferalSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = UserProfile
    fields = ['id', 'username', 'phone', 'email_confirmed']

class RefBonusSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = RefBonusAccount
    fields = ['id', 'username', 'refbonus', 'refoldbonus', 'redeemed', 'updated_date']

class NotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Notification
    fields = ['title', 'content', 'createdAt']
    
#===========================================================07/11/19
class SmsHistorySerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = SmsangoSendSMS
    fields = ['id', 'username', 'sender', 'recipients', 'messagecontent', 'status', 'creditusedall', 'sently', 'notsently', 'apiRoute', 'timestamp']

class CableApiSerializer(serializers.ModelSerializer):
  cable_type_price = serializers.SerializerMethodField()
  class Meta:
    model = CableRecharegAPI
    fields = ['api_name', 'identifier', 'cable_image', 'cable_type_price']

  def get_cable_type_price(self, obj):
    return json.loads(obj.cable_type_price)