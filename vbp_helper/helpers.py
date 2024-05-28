import datetime, pytz
from django.utils.crypto import get_random_string

def evalResponse(x):
  new_dict={}
  myprint(x, new_dict)
  return new_dict

def myprint(x, new_dict):
  my_list = x.items() if isinstance(x, dict) else enumerate(x)

  for k, v in my_list:
    if isinstance(v, dict) or isinstance(v, list):
      myprint(v, new_dict)
    else:
      new_dict[k]=v

def deleteSessions(list, request):
  try:
    for i in list:
      del request.session[i]
    return True
  except Exception as e:
    return False

def setSessions(keys, values, request):
  try:
    for i, j in (keys, values):
      request.session[i] = j
    return True
  except:
    return False


def generate_ordernumber(value):
    if value >= 10:
        return str(value)
    else:
        return str(0) + str(value)


def timezoneshit():
    d = pytz.timezone('Africa/Lagos')
    d = datetime.datetime.now(d)
    ordernumber = str(d.year) + generate_ordernumber(d.month) + generate_ordernumber(d.day) + generate_ordernumber(d.hour + 1) + generate_ordernumber(d.minute) + get_random_string(length=8)
    return ordernumber