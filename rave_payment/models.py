from django.db import models

class RaveConfiguration(models.Model):
    name = models.CharField(max_length=50, default="ravepay", help_text="Get the public and secret key here https://dashboard.flutterwave.com/dashboard/settings/apis")
    public_key = models.CharField(max_length=100,blank=True, null=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True)
    encryption_key = models.CharField(max_length=100, blank=True, null=True)
    rave_fee = models.FloatField(default=0.0, help_text="this is the fee ravepay charges in percentage so 0.09 means 9% of the funds to be paid")
    funding_limit = models.IntegerField(default=5000)

    def __str__(self):
        return str(self.name)

    class Meta:
      managed = True
      verbose_name = 'Rave Payment Configuration(Flutter Wave)'
      verbose_name_plural = 'Rave Payment Configuration(Flutter Wave)'

