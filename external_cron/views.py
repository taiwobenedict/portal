from django.shortcuts import render
from external_cron.models import Tasks,CompletedTasks
from django.http import JsonResponse, HttpResponse
import importlib
import json
from django.utils.crypto import get_random_string

def SMSTask(module, params):
  Tasks.objects.create(
    task_name = module,
    task_parameters = params,
    task_hash = get_random_string(length=15)
  )
  print('saved')
  return 'done'


def RunTask(request):
  get_tasks = Tasks.objects.filter(task_status='Not Done')
  for i in get_tasks:
    try:
      task_name = i.task_name.split('.')
      task_name = task_name[0] +'.'+ task_name[1]
      get_module = importlib.import_module(task_name)
      get_paramaters = i.task_parameters
      #.replace("'", '"').replace('"url_data": "', '"url_data": ')
      #get_paramaters = get_paramaters.replace('}}"', '}}')
      # print(get_paramaters, "==?")
      # vm = json.loads(get_paramaters)
      # print(vm, "=/?=?")
      v = get_paramaters
      print(v, v['recipients'], "=/?=?")
      CompletedTasks.objects.create(
        task_name = i.task_name,
        task_parameters = i.task_parameters,
        task_hash = i.task_hash,
      )
      i.delete()
      get_module.send_bulk_sms_bg(v['userid'],v['sender'], v['recipients'], v['numcount'], v['messagecontent'], v['smsroute'], v['totalsms'], v['opages'])
    except Exception as e:
      raise
  return HttpResponse('All Task Excuted')