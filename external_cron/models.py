from django.db import models

class Tasks(models.Model):
  task_name = models.CharField(max_length=100, default='')
  task_parameters = models.JSONField(default=dict)
  task_hash = models.CharField(max_length=20, default='')
  task_status = models.CharField(max_length=20, default='Not Done')
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.task_hash

  def __unicode__(self):
    return self.task_hash

class CompletedTasks(models.Model):
  task_name = models.CharField(max_length=100, default='')
  task_parameters = models.JSONField(default=dict)
  task_hash = models.CharField(max_length=20, default='')
  task_status = models.CharField(max_length=20, default='Done')
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.task_hash

  def __unicode__(self):
    return self.task_hash
