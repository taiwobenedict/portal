from django import template

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.
from notificationapp.models import *

register = template.Library()


@register.simple_tag(takes_context=True)
def getNoteReadNotification(context):
	request = context['request']
	user = request.user
	getNotReadNote = ReadNotification.objects.filter(user=user)
	getNote= Notification.objects.filter(~Q(readonly__in=getNotReadNote)).order_by('-createdAt')[:3]
	return getNote