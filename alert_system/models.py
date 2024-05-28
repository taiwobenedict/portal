from django.db import models
from django.contrib.auth.models import User

class AlertSystem(models.Model):
    title = models.CharField(max_length=100, default="")
    content = models.TextField(max_length="1000", default="", help_text="maximum character allowed is 1000")
    is_active = models.BooleanField(default=False) 
    display_times = models.IntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
      return self.title

    def __unicode__(self):
      return self.title

    class Meta:
      ordering = ("-created_at",)

class UserReadAlert(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_alert_read")
  alert = models.ForeignKey(AlertSystem, on_delete=models.CASCADE, related_name="system_alert")
  read_count = models.IntegerField(default=1)
  read_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.user.username + self.alert.title


class TutorialNews(models.Model):
  title = models.CharField(max_length=225, default="")
  url = models.URLField()
  pin_to_top = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return "{} | {}".format(self.title, self.url)

  class Meta:
    ordering = ('-created_at',)