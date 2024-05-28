from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Notification(models.Model):
	title = models.CharField(max_length=30, default="")
	content = models.TextField(default='', max_length=1000, blank=True, null=True)
	createdAt = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

class ReadNotification(models.Model):
	user = models.ForeignKey(User, related_name='readnotification', on_delete=models.CASCADE)
	read = models.ForeignKey(Notification, related_name='readonly', on_delete=models.CASCADE)
	readAt = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username