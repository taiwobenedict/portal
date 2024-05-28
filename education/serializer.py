from rest_framework import serializers
from education.models import *

#===========================================================07/11/19
class ResultCheckersSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  class Meta:
    model = ResultCheckers
    fields = ['id', 'username', 'amount', 'trans_id', 'pin_type', 'pin', 'serial_number', 'trans_id', 'status', 'date']