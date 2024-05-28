from django.db import models

class ErrorResponses(models.Model):
  name_of_api = models.CharField(default='', max_length=200)
  error_name = models.CharField(default="", max_length=200, blank=True, null=True)
  error_code = models.CharField(default="", max_length=200, blank=True, null=True)
  error_description = models.TextField(default="", blank=True, null=True)

  def __str__(self):
      return self.name_of_api
  