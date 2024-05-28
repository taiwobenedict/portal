from .models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts

def checkMesageLength(message_content):
  return True

def getApiObject(smsroute):
  print(smsroute)
  sendwithwhatApi = {}
  sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
  sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
  print(sendwithdnd)
  print(sendwithnotdnd)
  if len(sendwithdnd) == 0 or len(sendwithnotdnd) == 0:
    return 'SMS APIs has not been configured properly, Contact the Administrator'
  elif len(sendwithdnd) > 1:
    return 'More than 1 DND Apis has been activated, Contact the Administrator'
  elif len(sendwithnotdnd) > 1:
    return 'More than 1 NON DND Apis has been activated, Contact the Administrator'
  else:
    if smsroute in sendwithdnd[0].api_name:
      sendwithwhatApi['url'] = sendwithdnd[0].apurl
      sendwithwhatApi['url_data'] = sendwithdnd[0].apurl_data
      sendwithwhatApi['apiamtpersms'] = float(sendwithdnd[0].apiamtpersms)
      sendwithwhatApi['router'] = "DND ROUTE"
      sendwithwhatApi['api_response'] = sendwithdnd[0].api_response
      sendwithwhatApi['send_one_by_one'] = sendwithdnd[0].send_one_by_one
    elif smsroute == "NON_DND":
      sendwithwhatApi['url'] = sendwithnotdnd[0].apurl
      sendwithwhatApi['url_data'] = sendwithdnd[0].apurl_data
      sendwithwhatApi['apiamtpersms'] = float(sendwithnotdnd[0].apiamtpersms)
      sendwithwhatApi['router'] = "NON DND ROUTE"
      sendwithwhatApi['api_response'] = sendwithnotdnd[0].api_response
      sendwithwhatApi['send_one_by_one'] = sendwithdnd[0].send_one_by_one
    print(sendwithwhatApi)
    return sendwithwhatApi

def getMsgContent(messagecontent):
  messgcontentlength = len(messagecontent)
  opages = 4
  if messgcontentlength in range(0, 161):
    opages = 1
  elif messgcontentlength in range(161, 321):
    opages = 2
  elif messgcontentlength in range(321, 481):
    opages = 3

  return opages