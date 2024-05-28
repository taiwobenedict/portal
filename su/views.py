
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def ListAllUserToSwitch(request):
  if request.user.is_superuser:
    users = User.objects.all()
    return render(request, 'impersonate/list_users.html', {"users":users})
  return render(request, 'impersonate/list_users.html', {})

@login_required
def switch_user(request, username):
  if request.user.is_superuser:
    try:
      user = get_user_model().objects.get(username=username)
      auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
      return HttpResponseRedirect("/customer/")
    except User.DoesNotExist:
      pass
    # return HttpResponseRedirect("/customer/")
  raise Http404



