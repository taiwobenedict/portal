from rest_framework import serializers
from other_data_services.models import *

class SmileTransactionSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = SmileTransactions
    fields = ['id', 'username', 'numberRecharged', 'smileType', 'amount', 'trans_id', 'status', 'date']

class SpectranetTransactionsSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = SpectranetTransactions
    fields = ['id', 'username', 'numberRecharged', 'api_code', 'amount', 'trans_id', 'status', 'date']


class IntAirtimeTransactionsSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = IntAirtimeTransactions
    fields = ['id', 'username', 'numberRecharged', 'api_code', 'amount', 'trans_id', 'status', 'date']
