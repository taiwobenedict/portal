from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseRedirect
from django.contrib import messages
from django.core.mail import send_mail
from coreconfig.models import DashboardConfig
from mail.models import SmtpEmailSettings, SentEmails
from mail import tasks
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required(login_url=settings.LOGIN_URL)
def sendEmailTemplate(request):
  if request.method == 'POST':
    subject = request.POST['subject'].strip()
    message = request.POST['message'].strip()
    email = request.POST['user_email'].strip()
    send_all_users = request.POST.get('send_all_users')
    print(send_all_users)

    if send_all_users is None:
      print(subject, message, email)
      tasks.sending_mail(subject, message, [email])
      SentEmails.objects.create(email_subject=subject, email_content=message,\
        recipient=email, status="Been Sent")
    else:
      contact_list = []
      for i in User.objects.all():
        contact_list.append(i.email)
      tasks.sending_mail(subject, message, contact_list)
      SentEmails.objects.create(email_subject=subject, email_content=message,\
        recipient="All Users", status="Been Sent")
    messages.success(request,'message has been sent, if you dont get message within 15minutes check your configuration')
    return redirect('mailing:send_email')
  else:
    return render(request, 'mail/mailing.html', {})
  return render(request, 'mail/mailing.html', {})

# def sendMailOrMass(request):
#   try:
#     if request.method == 'POST':
#       subject = request.POST['subject'].strip()
#       message = request.POST['message'].strip()
#       email = request.POST['user_email'].strip()
#       tasks.sending_mail(subject, message, user.email)
#       return JsonResponse({'status':'','message':'', 'details':''})
#   except Exception as e:
#     pass
#   return JsonResponse({'status':'','message':'', 'details':''})
#   return JsonResponse({'status':'','message':'', 'details':''})
