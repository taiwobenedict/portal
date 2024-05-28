"""
WSGI config for smsango project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""
import os
import sys

sys.path.insert(0, '/home/django/smsangos/')

from django.core.wsgi import get_wsgi_application
# from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smsango.settings")

application = get_wsgi_application()
# application = DjangoWhiteNoise(application)


