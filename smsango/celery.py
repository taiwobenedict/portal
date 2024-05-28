# import os
# from celery import Celery


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smsango.settings')

# app = Celery('smsango')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_heartbeat=0
# app.autodiscover_tasks()