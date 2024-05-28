from rest_framework import serializers
from cryptocurrency.models import *

#===========================================================07/11/19
class CryptoCurrenciesSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = CryptoCurrencies
    fields = ['id', 'username', 'currency', 'company_name', 'trans_id', 'status', 'date']