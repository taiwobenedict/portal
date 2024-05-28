from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
from notificationapp.models import *


def detailNotification(request, pk):
	template_name = "notificationapp/detail.html"
	getNote = Notification.objects.get(pk=pk) 
	obj = ReadNotification.objects.create(
			user = request.user,
			read = getNote
		)
	return render(request, template_name,{'getNote': getNote})

def ListNotification(request):
	template_name = "notificationapp/list_notifications.html"
	getNote = Notification.objects.all() 
	return render(request, template_name,{'alerts': getNote})
