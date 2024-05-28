# howdy/urls.py
from django.conf.urls import url
from django.views.generic import TemplateView
# from howdy import views --- can be used also 
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views


from smsangonumcredit.views import *

#urlpatterns = [
 #   url(r'^$', views.HomePageView.as_view()),
 #   url(r'^daabout/$', views.AboutPageView.as_view()),
 #   url(r'^about/$', views.About.as_view()),
 #   url(r'^contact/$', views.Contact.as_view()), # Add this /about/ route
#]
