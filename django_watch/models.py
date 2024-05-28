from django.db import models


class DjangoWatch(models.Model):
  li_value = models.CharField(max_length=50)
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.li_value

  def __unicode__(self):
      return self.li_value
