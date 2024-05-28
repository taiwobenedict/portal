from django import template

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.
from coreconfig.models import *

register = template.Library()


@register.simple_tag()
def DashboardConfigs():
	try:
		dashboardConfig = DashboardConfig.objects.all()
		return dashboardConfig[0]
	except Exception as e:
		return ''

@register.filter
def multiply(value, arg):
    return value * arg

@register.simple_tag()
def DisplayAppsConfig():
	try:
		displays = DisplayOfApps.objects.all()
		return displays[0]
	except Exception as e:
		return ''


@register.simple_tag()
def DisplayAppsConfigDashboard():
	displays = DisplayOfApps.objects.all()
	try:
		return displays[0]
	except Exception as e:
		return ''