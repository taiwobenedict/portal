from django import template
from django.db.models import Q
from rave_payment.models import *

register = template.Library()


@register.simple_tag
def RavePayConfigs():
	try:
		rave_pay_config = RaveConfiguration.objects.all()
		return rave_pay_config[0]
	except Exception as e:
		return ''