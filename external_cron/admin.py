from django.contrib import admin

from external_cron.models import Tasks, CompletedTasks

admin.site.register(Tasks)
admin.site.register(CompletedTasks)