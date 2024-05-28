from rest_framework import serializers
from electricity.models import *

#===========================================================07/11/19
class electricitySerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = Electricity
    fields = ['id', 'username', 'email', 'phone', 'amount', 'service', 'meter_no', 'customer_name', 'customer_address', 'customer_account_type', 'customer_dt_number', 'trans_id', 'date']

class electricityApiSerializer(serializers.ModelSerializer):
  class Meta:
    model = ElectricityApis
    fields = ['api_name', 'identifier', 'electricity_image', 'electricity_code_json']
