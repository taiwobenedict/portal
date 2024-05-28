from django import template
from django.db.models import Q
from django.utils import timezone
import datetime
from django.utils.html import format_html
from other_data_services.models import IntAirtimeApi
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def site_commission(id):
	apiInt = IntAirtimeApi.objects.filter(is_active=True)
	if apiInt.exists():
		apiInt = apiInt.first()
		return  apiInt.commission
	else:
		return 0
