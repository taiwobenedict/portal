from django import template
from django.db.models import Q
from alert_system.models import *

register = template.Library()

@register.inclusion_tag('alert_system/alert_system.html', takes_context=True)
def display_the_alert(context):
	request = context['request']
	get_alert = AlertSystem.objects.filter(is_active=True).order_by("created_at")
	get_user_alert = UserReadAlert.objects.filter(alert=get_alert.first(), user=request.user)

	try:
		if len(get_user_alert) > 0:
			return {
				'alert_present': True,
				'alert_sys': get_alert.first(), 
				'user_alert': get_user_alert[0]
				}
		else:
			return {
				'alert_present': True,
				'alert_sys': get_alert.first(), 
				'user_alert': "display"
				}
	except:
		print("issues")
		return {
			'alert_present': False
			}