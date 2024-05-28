import os
from django.core.files import File
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django_watch.models import DjangoWatch
from django_watch.forms import DjangoWatchForm
from django.views.decorators import csrf
from django.shortcuts import redirect


def get_or_none(livalue):
  try:
    obj = DjangoWatch.objects.all()
    if len(obj) == 0:
      return None
    else:
      return obj[0].li_value
  except Exception as e:
    return None

class CheckLiValueMiddleware:
  def __init__(self, get_response):
    try:
      self.get_response = get_response
      open_code = open(os.path.join(os.getcwd(), 'code.txt'), 'r')
      contents = open_code.readlines()
      values = [line for line in contents][0]
      open_code.close()
      getlivalue = get_or_none(values)
      if getlivalue != None and getlivalue == values:
        self.liveli_value = True
      else:
        self.liveli_value = False
    except Exception as e:
      self.liveli_value = False

  def __call__(self, request):
    response = self.get_response(request)
    return response

  # def process_view(self, request, view_func, *view_args, **view_kwargs):
  #   if self.liveli_value == False:
  #     context = {}
  #     context['django_form'] = DjangoWatchForm()
  #     context['csrf_token'] = csrf.get_token(request)
  #     # context['site_config'] = DjangoWatchForm
  #     return SimpleTemplateResponse('admin/admin.html', context)
  #   else:
  #     pass

  def process_template_response(self, request, response):
    if self.liveli_value == False:
      context = {}
      context['django_form'] = DjangoWatchForm()
      context['csrf_token'] = csrf.get_token(request)
      return SimpleTemplateResponse('django_watch/admin.html', context)
    else:
      return response

