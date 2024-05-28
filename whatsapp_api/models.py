from django.db import models
from django.contrib.auth.models import User

class WhatsAppPurchaseAccess(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_whatsapp_access')
	pin = models.CharField(max_length=6, default='')
	is_active = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username
		
class WhatsAppSettings(models.Model):
	app_code = models.CharField(max_length=20, default='whatsapp')

	def __str__(self):
		return self.app_code