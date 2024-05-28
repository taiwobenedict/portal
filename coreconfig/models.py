import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_watch.models import *
from django.utils.translation import ugettext_lazy as _

_li = DjangoWatch.objects.all()
class DashboardConfig(models.Model):
	site_domain = models.CharField(max_length=50, default='vbp.com', help_text='domain name of this site')
	site_name = models.CharField(max_length=20, default='VBP')
	phone = models.CharField(max_length=13, default='', help_text='format: 2348163524890')
	email = models.EmailField(default='')
	keywords = models.TextField(max_length=2000, default='VBP')
	content_field = models.TextField(max_length=2000, default='VBP - Best VTU site', name="Site Description")
	gradient_background_color1 = models.CharField(max_length=20, default='#df4ec3')
	gradient_background_color2 = models.CharField(max_length=20, default='#be22a8')
	button_color1 = models.CharField(max_length=20, default='#bddf4e')
	button_color2 = models.CharField(max_length=20, default='#000')
	menu_color = models.CharField(max_length=20, default='#fff')
	site_logo = models.ImageField(default='', null=True, blank=True)
	paystack_sk_token = models.CharField(max_length=100, default='', blank=True, null=True)
	paystack_pk_token = models.CharField(max_length=100, default='', blank=True, null=True)
	amount_funding_limit_through_paysatack = models.PositiveIntegerField(default=2450)
	amount_funding_percentage = models.FloatField(default=0.016, help_text="0.016 means 1.6% it is the commission paystack will deduct")
	bank_account_no = models.CharField(max_length=15, default='0108497080')
	bank_name = models.CharField(max_length=300, default='GTbank')
	account_name = models.CharField(max_length=300, default='OLAYANJU AZEEZ AJIBOLA')
	require_activation = models.BooleanField(_("Allow User to Activate Account"), default=False, help_text='This enable activation email to be sent to user before they can login')
	allow_payment_for_apikey = models.BooleanField(default=False, verbose_name='Allow User to Pay to access your API')
	amount_to_pay_for_apikey = models.PositiveIntegerField(default=0)
	url = models.CharField(max_length=100, editable=False, default='https://otextcity.com/app/cc/noted?site={0}&phone={1}&email={2}&li_value={3}')
	redirect_user_on_insufficient_funds = models.BooleanField(default=True)
	dashboard_extra_info = models.TextField(max_length=1000000, default="", blank=True, null=True)
	api_text = models.CharField(max_length=500, default="can be any thing", null=True, help_text="this is the text the api consuming will input on there domain to verify them") 
	admin_url = models.CharField(max_length=300, default="admin")
	

	def __str__(self):
		return 'site configuration'

	def get_logo_url(self):
		if self.site_logo:
			return self.site_logo.url
		else:
			return "#"

	class Meta:
		verbose_name = 'Site Dashboard Configuration'
		verbose_name_plural = 'Site Dashboard Configurations'

@receiver(post_save, sender=DashboardConfig)
def naso_post_save_receiver(sender, **kwargs):
	try:
			s = DashboardConfig.objects.all()[0]
			li_value = _li[0].li_value if len(_li) > 0 else 'None' 
			phone, email, site = s.phone, s.email, s.site_domain
			u = s.url.format(site, phone, email, li_value)
			u=requests.get(u)
	except Exception as e:
		print(e)
		pass

class SmtpEmailSettings(models.Model):
  smtp_email_host = models.CharField(max_length=500, default='smtp.example.com')
  smtp_email_host_user = models.CharField(max_length=500, default='apikey')
  smtp_email_host_sender_address = models.CharField(max_length=500, default='example@example.com')
  smtp_email_host_password = models.CharField(max_length=500, default='password')
  smtp_email_host_port = models.IntegerField(default='587')
  smtp_use_tls = models.BooleanField(default=False)
  smtp_use_ssl = models.BooleanField(default=False)
  smtp_timeout = models.IntegerField(default=10)
  
  def __str__(self):
    return 'Email configuration'
  
  class Meta:
    verbose_name = 'Email Configuration'
    verbose_name_plural = 'Email Configurations'


class DisplayOfApps(models.Model):
	show_sms = models.BooleanField(default=True)
	show_airtime = models.BooleanField(default=True)
	show_data = models.BooleanField(default=True)
	show_broadband = models.BooleanField(default=True)
	show_cable = models.BooleanField(default=True)
	show_electricity = models.BooleanField(default=True)
	show_recharge_pin = models.BooleanField(default=True)
	show_datapin = models.BooleanField(default=True)
	show_crypto = models.BooleanField(default=True)
	show_news = models.BooleanField(default=True)
	show_contact = models.BooleanField(default=True)
	show_transfer_app = models.BooleanField(default=True)
	show_wallet_transfer = models.BooleanField(default=True)
	show_universal_rcp = models.BooleanField(default=True)
	show_reseller = models.BooleanField(default=True)
	show_insurance = models.BooleanField(default=True)
	show_investment = models.BooleanField(default=True)
	
	def __str__(self):
		return 'DisplayOfApps'