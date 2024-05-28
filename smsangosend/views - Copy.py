from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.core.validators import RegexValidator
import random
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, CreateView
import re
import requests, datetime
from django.utils.crypto import get_random_string
# from datetime import 
from django.views import View
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text, smart_text 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
UserModel = get_user_model() 
from django.contrib.auth.models import User
from django.views import generic
from rechargeapp.utility import get_or_none
from .forms import *
from .models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import PricingPerSMSPerUserToPurchase, DefaultPricePerSMSToPurchase
from payments.models import *
import decimal
from  more_itertools import unique_everseen
from django.contrib import messages
from smsangosend.tasks import send_bulk_sms_bg, SendScheduledSMS_bg
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge
from smsangonumcredit.models import BonusesPercentage
from coreconfig.models import *
from django.conf import settings


def signup(request):
    refferal = request.GET.get('refferal')
    if request.method == 'POST':
    	phone = (request.POST.get('phone')).strip()
    	checkPhone = get_or_none(UserProfile, phone=phone)
    	form = SignUpForm(request.POST)
    	if checkPhone is not None:
      		return render(request, 'registerpage.html', {'Error':'A user with that Phone Number already exist'})
    	elif len(phone) < 13 or len(phone) > 13:
      		return render(request, 'registerpage.html', {'Error':'Invalid Phone Number'})
    	else:
    		if form.is_valid():
    			user = form.save(commit=False)
    			user.is_active = True
    			user.save()
    			user.userprofile.refferal = refferal
    			user.userprofile.phone = phone
    			user.userprofile.save()
    			current_site = get_current_site(request)
    			config = DashboardConfig.objects.all()
    			uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
    			if len(config) == 0:
    				subject = 'Activate Your VBP Account'
    				message = render_to_string('account_activation_email.html',{
    					'user': user,'domain': current_site.domain,'uid': uid,'token': account_activation_token.make_token(user),
	    			})
	    			user.email_user(subject, message)
    			else:
    				subject = 'Activate Your' + config[0].site_name + 'Account'
    				message = render_to_string('account_activation_email.html',{
    					'user': user,'domain': current_site.domain,'uid': uid,'token': account_activation_token.make_token(user),
	    			})
	    			user.email_user(subject, message)
    			return redirect('smsangosend:account_activation_sent')
    else:
    	form = SignUpForm()
    context	= {
		'register_form': form,
		'referral':refferal,
    }
    return render(request, 'registerpage.html', context)

def activate(request, uidb64, token):
    try:
    	uid = force_text(urlsafe_base64_decode(uidb64))
    	user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):    	
        user.is_active = True
        user.save()
        user.userprofile.email_confirmed = True
        user.userprofile.save()
        try:
        	getref = get_object_or_404(UserModel, username=user.userprofile.refferal)
        	getbonuspercent = get_or_none(BonusesPercentage, is_active=True)
        	amt_to_bonus = 0 if getbonuspercent is None else getbonuspercent.referral_bonus
        	getref.user_bonus.bonus += decimal.Decimal(float(amt_to_bonus))
        	getref.user_bonus.save()
        	print(getref.user_bonus.bonus)
        except Exception as e:
        	pass
        #Create the user credit profile#################
        de = SmsangoSBulkCredit.objects.get(user=user)
        getbonuspercent = get_or_none(BonusesPercentage, is_active=True)
        amt_to_bonus = 0 if getbonuspercent is None else getbonuspercent.signup_bonus
        de.smscredit = decimal.Decimal(float(amt_to_bonus))
        de.save()
        current_site = get_current_site(request)
        config = DashboardConfig.objects.all()
        if len(config) == 0:
	        subject = 'Your VBP Account is Activated'
	        message = render_to_string('account_activation_email_followup.html', {
	        	'user': user,
	        	'domain': current_site.domain,
	        	})
	        user.email_user(subject, message)
        else:
	        subject = 'Your' + config[0].site_name + 'Account is Activated'
	        message = render_to_string('account_activation_email_followup.html', {
	        	'user': user,
	        	'domain': current_site.domain,
	        	})
	        user.email_user(subject, message)
		##############################################
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect('/customer/profile-edit')
    else:
        return render(request, 'account_activation_invalid.html')

def get_absolute_url(self):
		return reverse('smsangosend:activate')

@login_required(login_url='/customer/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('smsangosend:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'acc/change_password.html', {
        'form': form
    })


@login_required(login_url='/customer/login')
def Home(request):
    return redirect('/customer/')

#SEND SMS VIEW CODED#################
@login_required(login_url='/customer/login')
def SmsangoSendSMS_createview(request):
	instance = request.user
	userid = int(instance.id)
	# print (userid)
	if not instance.userprofile.phone:
		messages.success(request, 'Update your profile to proceed')
		return HttpResponseRedirect('/customer/profile-edit')

	careful = None
	successdety = None
	successde = None
	# status = None
	template_name = "sendsms.html"
	lphc = PhoneBookContacts.objects.filter(user=instance)
	if request.method == "POST":		
		# form = SmsangoSendSMSForm(request.POST or request.FILES)
		form = SmsangoSendSMSForm(request.POST or None)
		if form.is_valid():
			instance = (instance)
			# print (instance)
			sender = request.POST.get("sender")
			recipients = request.POST.get("recipients")
			messagecontent = request.POST.get("messagecontent")
			messagecontent = messagecontent.strip()			
			smsroute = request.POST.get("smsroute")
			if smsroute == "DND":
				sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
				for i in sendwithdnd:
					oto = i.apurl
					apiamtpersms = i.apiamtpersms
					router = "DND ROUTE"
					# print ("send with dnd" + oto )
			else:
				sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
				print(sendwithnotdnd)
				for i in sendwithnotdnd:
					oto = i.apurl
					apiamtpersms = i.apiamtpersms
					router = "NON DND ROUTE"
					# print ("send without dnd" + oto )
			numcount = recipients.split(',')
			messgcontentlength = len(messagecontent)
			if messgcontentlength < 161:
				opages = 1
			elif messgcontentlength > 160 and messgcontentlength < 321:
				opages = 2
			elif messgcontentlength > 320 and messgcontentlength < 481:
				opages = 3
			else:
  				successde = "You can only send a maximum of 3 pages at once"
  				return render(request, template_name, {"successde":successde})
			print(opages)
			numlength = len(numcount)
			if numlength > 200:
  				successde = "You can only send to a maximum of 200 recipients at once"
  				return render(request, template_name, {"successde":successde})
      #get the total amount of credit to be used during the sms campaign
			totalsms = (numlength * apiamtpersms * opages)
			print(totalsms)
			rt = SmsangoSBulkCredit.objects.get(user=instance)
			rtcredit = rt.smscredit
			# print(rt.smscredit)
			if int(totalsms) > float(rt.smscredit):
				successde = "You are low on credit, purchase sms units to send sms" 
				#RETREIVE CREDIT FROM DATABASE, SUBTRACT FROM THE MESSAGE SENT AND UPDATE THE DATE BASE BACK WITH THE NEW CREDITS
				# SCredit =
				context = { "careful": careful, "successdety":successdety, "successde":successde, "lphc":lphc }
				return render(request, template_name, context)
			else:
				send_bulk_sms_bg.delay(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, rtcredit, oto, router, apiamtpersms)
				successde = str(numlength) + " Messages are being sent in background Check <a href='/customer/smshistory'>SMS Report</a> for full details" 
				context = { "careful": careful, "successdety":successdety, "successde":successde, "lphc":lphc }
				return render(request, template_name, context)
	return render (request, template_name, {"lphc":lphc } )


@login_required(login_url='/customer/login')
def SmsHistory_listview(request):
	template_name = 'smshistory.html'
	queryset = SmsangoSendSMS.objects.filter(user=request.user).order_by('-timestamp')
	paginator = Paginator(queryset, 1000)#show 20 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)
	return render(request, template_name, {'historys': historys, })

@login_required(login_url='/customer/login')
def SmsReport_listview(request):
	template_name = 'smsreport.html'
	queryset = SmsangoSendSMS.objects.filter(user=request.user).order_by('-timestamp')[:10]
	paginator = Paginator(queryset, 1000)#show 20 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)

	context = {
		"historys": historys
	}
	return render(request, template_name, context)

@login_required(login_url='/customer/login')
def SmsIndividualReport(request, pk):
	template_name = 'smsindireport.html'
	indsmsreport = SmsangoSendSMS.objects.get(pk=pk, user=request.user, )
	context = {
		'indsmsreport':indsmsreport
	}
	return render(request, template_name, context)


@login_required(login_url='/customer/login')
def Dashboard_View(request):
	template_name = "dashboard.html"
	jonep = request.user
	d = SmsangoSBulkCredit.objects.get_or_create(user=jonep)
	numb = UserProfile.objects.get_or_create(user=jonep)
	getallreffered = UserProfile.objects.filter(refferal=jonep.username)
	context = {
		"pcredit": d,
		"numb":numb,
		"getallreffered":len(getallreffered),
	}
	return render (request, template_name, context)

@login_required(login_url='/customer/login')
def Phonenumber_view(request):
	# user = auth.authenticate(username=username, password=password)
	# g = user.userprofile.phone
	# print (g)
	template_name = "phone.html"
	if request.method == "POST":
		form = PhoneForm(request.POST or None)
		if form.is_valid():
			user = User.objects.get(id=request.user.id)
			print (user)
			phone = request.POST.get("phone")
			print (phone)
		instance = UserProfile.objects.get(user=(user))
		instance.phone = form.cleaned_data.get('phone')
		instance.save()
		return HttpResponseRedirect('/customer/')
	return render (request, template_name)	

############## THIS IS FOR THE PHONE NUMBER EXTRATOR ###############
##---THE BELOW IS TO CREATEA A REUSABLE FUNCTION ---##

#++++ This Extracts the numbers WITH "234" from any file ++++#
# @login_required(login_url='/customer/login/')
def ExtractNumberwithPrefix(recipien):
	phoneNumRegex = re.compile(r'234\d\d\d\d\d\d\d\d\d\d')#this search for numbers with 234 prefix 
	matches = []
	for i in phoneNumRegex.findall(recipien):
		phoneNum = ''.join([i[0], i[1], i[2],i[3],i[4],i[5],i[6], i[7], i[8], i[9], i[10],i[11],i[12]])
		matches.append(phoneNum)
	processrecipients = ((',\n'.join (matches)))	
	return processrecipients.strip()

#++++ This replaces "234" with "0" ++++#
# @login_required(login_url='/customer/login/')
def RemovePrefix(recipien):
	phoneNumRegex= re.compile(r'\b234')#this search for number with 234 alone
	recipients = phoneNumRegex.sub(r'0',recipien, count=0)#this replaces it with '0' as starting letter
	phoneNumRegex = re.compile(r'0\d\d\d\d\d\d\d\d\d\d')
	matches =[]
	for i in phoneNumRegex.findall(recipients):
		phoneNum = ''.join([i[0], i[1], i[2],i[3],i[4],i[5],i[6], i[7], i[8], i[9], i[10]])
		matches.append(phoneNum)
	processrecipients = ((',\n'.join (matches)))
	return processrecipients.strip()		

#++++ This replaces "0" with "234" ++++#
def substitut(recipien):
	phoneNumRegex= re.compile(r'\b0')#this search for number with 234 alone
	recipients = phoneNumRegex.sub(r'234',recipien, count=0)#this replaces it with '0' as starting letter
	phoneNumRegex = re.compile(r'234\d\d\d\d\d\d\d\d\d\d')
	matches =[]
	for i in phoneNumRegex.findall(recipients):
		phoneNum = ''.join([i[0], i[1], i[2],i[3],i[4],i[5],i[6], i[7], i[8], i[9], i[10],i[11],i[12]])
		matches.append(phoneNum)
	processrecipients = ((',\n'.join (matches)))	
	return processrecipients.strip()		

#Remove Duplicates
def Removeduplicate(recipien):
	match = list(unique_everseen(recipien))		
	matches = []
	for i in match:
    		matches.append(i)
	processrecipients=((','.join (matches)))
	return processrecipients.strip()	


@login_required(login_url='/customer/login')
def Phonenumberextractor(request):
	instance = request.user
	if not instance.userprofile.phone:
		messages.success(request, 'Update your profile to proceed')
		return HttpResponseRedirect('/customer/profile-edit')
	template_name="phonenumberextrator.html"
	if request.method == "POST":
		recipients = request.POST.get("recipients")
		operations = request.POST.get("operations")
		if operations == "Addprefix":
			phoneextracted = substitut(recipients)#This is used to add prefix to the numbers
			lent = phoneextracted.split(',')
			processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
		elif operations == "extractwithprefix":
			phoneextracted = ExtractNumberwithPrefix(recipients)#This is used to extract numbers with prefix to the numbers
			lent = phoneextracted.split(',')
			processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
		elif operations == "Removeprefix":
			phoneextracted = RemovePrefix(recipients)
			lent = phoneextracted.split(',')
			processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
		elif operations == "Removeduplicate":
			recip = recipients.split(',')
			print(recip)
			phoneextracted = Removeduplicate(recip)
			lent = phoneextracted.split(',')
			processed = str(len(lent)) + " NUMBERS WAS PROCESSED! DUPLICATES REMOVED"
		else:
			processed = "SOMETHING WENT WRONG"
		context = {
			"recipients":recipients,
			"phoneextracted":phoneextracted,
			"processed":processed
		}
		template_name="phonenumberextrator.html"
		return render (request, template_name, context)
	return render (request, template_name)
##############################THE ABOVE IS IN USE NOW #####################
######################DUPLICATE REMOVAL#########################################

##########################################################
#---------------------------------------------------------#
####### Saving Phone book #########
@login_required(login_url='/customer/login')
def PhoneBookContactsView(request):
	template_name = 'phonebookcontact.html'
	instance = request.user	
	if not instance.userprofile.phone:
		messages.success(request, 'Update your profile to proceed')
		return HttpResponseRedirect('/customer/profile-edit')
	phc = PhoneBookContacts.objects.filter(user=instance)
	idname = []
	name = []
	counted_contacts = []
	for j in phc:
		aj = j.name_contacts
		idj = j.id
		cn = j.contact_numbers
		cox = cn.split(',')
		coxlen = len(cox)
		name.append(aj)
		counted_contacts.append(coxlen)
		idname.append(idj)

	if request.method == "POST":
		form = PhoneBookContactsForm(request.POST, request.FILES or None)
		if form.is_valid():
			instance = instance
			contact_numbers = request.POST.get("contact_numbers")
			name_contacts = request.POST.get("name_contacts")
			uploadedfile = request.FILES.get("uploadcontacts", '')
			if uploadedfile:
				try:
					if not uploadedfile.name.endswith('.txt'):
						messages.error(request, 'Upload .txt file please')
						return redirect('smsangosend:phonebooks')
					elif uploadedfile.multiple_chunks():
						messages.error(request, "Uploaded file is too big (%.2f MB)." % (uploadedfile.size/(1000*1000),))
						return redirect('smsangosend:phonebooks')
					else:
						uplod = uploadedfile.read().decode("utf-8")
						uplos = uplod.strip()
						print (uplos)
						obj = PhoneBookContacts. objects.create(
							user = (instance),
							contact_numbers = uplos,
							name_contacts = name_contacts,
						)
						messages.success(request, 'Contacts successfully saved')
						return redirect('smsangosend:phonebooks')
				except:
					pass
			elif contact_numbers:
				obj = PhoneBookContacts. objects.create(
					user = (instance),
					contact_numbers = contact_numbers,
					name_contacts = name_contacts,
				)
				messages.success(request, 'Contacts successfully saved')
				return redirect('smsangosend:phonebooks')
	else:
		form = PhoneBookContactsForm()
		context={
			'form':form,
			'phc': phc,
			'phk':zip(name, counted_contacts, idname),
			# 'messages':messages
		}
		return render(request, template_name, context)
	return render(request, template_name)

@login_required(login_url='/customer/login')
def PhoneBookContactsViewEdit(request, pk):
	number_instance = get_object_or_404(PhoneBookContacts, pk=pk)
	if request.method == 'POST':
		edit_contact_form = PhoneBookContactsEditForm(request.POST or None)
		if edit_contact_form.is_valid():
			name_contacts = request.POST.get('name_contacts')
			contact_numbers = request.POST.get('contact_numbers')
			obj, created = PhoneBookContacts.objects.update_or_create(pk=pk, user=request.user, defaults={'name_contacts':name_contacts, 'contact_numbers':contact_numbers})
			messages.success(request,'Contacts Updated!')
			return redirect('smsangosend:phonebooks')
		else:
			messages.error(request,'Please correct the error below.')
	return render(request, 'edits/edit_contact_form.html', {
		'name': number_instance.name_contacts,
		'numbers': number_instance.contact_numbers,
	})

@login_required(login_url='/customer/login')
def Contact_Delete(request, pk, template_name='edits/contacts_confirm_delete.html'):
    delcontact= get_object_or_404(PhoneBookContacts, pk=pk)    
    if request.method=='POST':
        delcontact.delete()
        return redirect('smsangosend:phonebooks')
    return render(request, template_name, {'delcontact':delcontact})

@login_required(login_url='/customer/login')
def LoadNumbersFromSelectedList(request):
    getphoneid = request.GET.get('phonebook', None)
    phcnumber = PhoneBookContacts.objects.get(id=int(getphoneid))
    return render(request, 'partials/dropdown_option.html' , {'phcnumber':phcnumber})

#PURCHASE SMS CREDITS
import random
import string

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url='/customer/login')
def FisrtPriceChoicePlan(request):
	template_name='paystack/select_plan.html'
	return render(request, template_name)

@login_required(login_url='/customer/login')
def PriceChoicePlan(request):
	template_name = 'paystack/payment_page.html'
	user=request.user
	if not user.userprofile.phone:
		return HttpResponseRedirect('/customer/profile-edit')	
	# print(user)
	if request.method=="POST":
		amounttobuy = request.POST.get('amounttobuy')
		orderid = random_string_generator(size=20)
		if int(amounttobuy) > 2450:
			return render(request, 'paystack/select_plan.html', {'message':'The highest Amount you can pay once is #2450 per transaction'})
		else:
			try:
				getuserspecificprice = PricingPerSMSPerUserToPurchase.objects.get(user=user)
				cedituser = getuserspecificprice.price
				context = {
					'getuserspecificprice':cedituser,
					'amounttobuy':((float(amounttobuy)*float(0.015))+float(amounttobuy))*100,
					'amounttobuyy':((float(amounttobuy)*float(0.015))+float(amounttobuy)),
					'orderid': orderid,
					'realamounttobuy': amounttobuy,
				}
				return render(request, template_name, context)
			except ObjectDoesNotExist:
				getdefaultprice = DefaultPricePerSMSToPurchase.objects.get(is_active=True)

				context = {
					'getuserspecificprice':float(getdefaultprice.priceperunit),
					'amounttobuy':((float(amounttobuy)*float(0.015))+float(amounttobuy))*100,
					'amounttobuyy':((float(amounttobuy)*float(0.015))+float(amounttobuy)),
					'orderid': orderid,
					'realamounttobuy': amounttobuy,
				}
				return render(request, template_name, context)
		return render(request, template_name)
	return render(request, template_name)
	# totalamount = float(amounttobuy)*100

from .tokens import TokenAuth
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
def PaystackSuccess(request):
	amountfrompayst = request.session['amount']
	updatesmscredit = request.session['newbalance']
	reference = request.session['reference']
	template_name = 'paystack/success_page.html'
	context = {
		'amountfrompayst':amountfrompayst,
		'reference': reference,
		'updatesmscredit': updatesmscredit
	}
	return render(request, template_name, context)

def PaystackFailure(request):
	template_name = 'paystack/failure.html'
	return render(request, template_name, {})
# 	return render(request, template_name, context)
@login_required(login_url='/customer/login')
def PaystackCallBack(request):
	usertocredit = request.user
	userid = request.POST['id']
	orderid = request.POST['trxref']
	reference = request.POST['reference']
	amount = request.POST['amount']
	price = request.POST['price']
	realamounttobuy = request.POST['realamount']
	url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
	r = requests.get(url, auth=TokenAuth(DashboardConfig.objects.all[0].paystack_sk_token))
	print(r.content)
	response = json.loads(r.text)
	#print(response['data']['status'] == 'success')
	if int(usertocredit.id) == int(userid) and response['data']['status'] == 'success':
		amountfrompayst = float(realamounttobuy)/100
		amtcredited = round((float(realamounttobuy)/float(price)),2)
		get_user = SmsangoSBulkCredit.objects.get(user=usertocredit)
		# print(get_user)
		obj = PayStackPayment.objects.create(
			user = usertocredit,
			smsangosbulkcredit = get_user,
			order_id = orderid,
			amtcredited = amtcredited,
			amount = realamounttobuy,
			reference = reference,
		)
		# amtotcredit = float(amount)/float(price)
		updatesmscredit = float(get_user.smscredit) + float(amtcredited)
		get_user.smscredit = updatesmscredit
		get_user.save()
		request.session['amount'] = realamounttobuy
		request.session['newbalance'] = updatesmscredit
		request.session['reference'] = reference
		context = {
			'status': response['data']['status'],
			'orderid':orderid,
			'amount':realamounttobuy,
			'amtotcredit':realamounttobuy,
			'updatesmscredit':updatesmscredit,
		}
		return JsonResponse(context, safe=False)
	else:
		return JsonResponse({'error': 'failed'}, safe=False)
	return JsonResponse({'error': 'failed'}, safe=False)

@login_required(login_url='/customer/login')
def PaymentHistory(request):
	user = request.user
	userpay_history = PayStackPayment.objects.filter(user=user).order_by('-dated')
	paginator = Paginator(userpay_history, 1000)#show 20 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)

	context = {
		"historys": historys
	}	
	return render(request, 'paystack/payment_history.html', context)

@login_required(login_url='/customer/login')
def UserProfileUpdates(request):
	user = request.user
	get_profile = UserProfile.objects.get(user=user)
	if request.method == 'POST':
		user_form = UserUpdateForm(request.POST, instance=user)
		profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.userprofile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, ("Your Profile has been Updated !!"))
			return redirect("smsangosend:profile_edit")
		else:
			messages.error(request, ("Please Correct the error below"))
	else:
		user_form = UserUpdateForm(instance=user)
		profile_form = ProfileUpdateForm(instance=user.userprofile)
	template_name = 'profile.html'
	return render(request, template_name, {'user_form':user_form, 'profile_form':profile_form, 'get_profile':get_profile})

################THIS PART IS FOR SMS SCHEDULING#########
import pytz
utc=pytz.UTC

@login_required(login_url='/customer/login')
def SavedScheduleSMS(request):
	template_name='schedule/schedulesms.html'
	user = request.user
	print('passed 1')
	if not user.userprofile.phone:
		return HttpResponseRedirect('smsangosend:profile_edit')
	lphc = PhoneBookContacts.objects.filter(user=user)
	print('passed 2')
	if request.method == 'POST':
		sender = request.POST.get("sender")
		recipients = request.POST.get("recipients")
		messagecontent = request.POST.get("messagecontent")
		time_to_send = request.POST.get("time_to_send")
		smsroute = request.POST.get("smsroute")
		print(sender,recipients,messagecontent,time_to_send,smsroute)
		if smsroute == "DND":
			sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
			for i in sendwithdnd:
				oto = i.apurl
				apiamtpersms = i.apiamtpersms
				router = "DND ROUTE"
		else:
			sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
			for i in sendwithnotdnd:
				oto = i.apurl
				apiamtpersms = i.apiamtpersms
				router = "NON DND ROUTE"
				print ("send without dnd" + oto )
			numcount = recipients.split(',')
			messgcontentlength = len(messagecontent)
			if messgcontentlength in range(1, 160):
				opages = 1
			elif messgcontentlength in range(161, 320):
				opages = 2
			elif messgcontentlength in range(321, 480):
				opages = 3
			print(opages)
		numcount = recipients.split(',')
		print(numcount)
		totalsms = (len(numcount) * apiamtpersms)
		print(totalsms)
		rt = SmsangoSBulkCredit.objects.get(user=user)
		print(rt.smscredit)
		chk = int(totalsms) > int(rt.smscredit)
		print(chk)
		if int(totalsms) > int(rt.smscredit):
				successde = "You are low on credit, purchase sms units to send sms" 
				#RETREIVE CREDIT FROM DATABASE, SUBTRACT FROM THE MESSAGE SENT AND UPDATE THE DATE BASE BACK WITH THE NEW CREDITS
				# SCredit =
				context = { "careful": careful, "successdety":successdety, "successde":successde, "lphc":lphc }
				return render(request, template_name, context)
		else:
			print('inside the if condition')
			datetime_obj = datetime.datetime.strptime(time_to_send, "%Y-%m-%d %H:%M:%S")
			datetime_obj_utc = datetime_obj.replace(tzinfo=utc)
			print(datetime_obj_utc)
			with transaction.atomic():
				obj = SavedScheduledSMS.objects.create(
					user = user,
					sender = sender,
					recipients = recipients,
					messagecontent = messagecontent,
					time_to_send = datetime_obj_utc,
					smsroute = smsroute,
					scheduleidnum = get_random_string(length=14),
				)
			time_to_sendd = SavedScheduledSMS.objects.get(user=user, time_to_send=time_to_send)
			successde = "SMS has been scheduled to sent at exactly " +  str(time_to_sendd.time_to_send)
			print('successde')
			return render(request, template_name, {'lphc':lphc, 'successde':successde})	
	else:
		print('Else thing')
		return render(request, template_name, {'lphc':lphc })
	return render(request, template_name, {'lphc':lphc })

# @login_required(login_url='/customer/login')
def SchedulingSMS(request):
	careful = None
	successdety = None
	successde = None
	timenow = timezone.now()
	difftime = datetime.timedelta(minutes=60)
	futuretime = (timenow + difftime)
	get_schedulemsg = SavedScheduledSMS.objects.filter(time_to_send__gte=timenow, status=False)
	# print(get_schedulemsg)
	for n in get_schedulemsg:
		userid = n.user.id
		if n.time_to_send >= timenow and n.time_to_send <= futuretime:
			sender = n.sender
			recipients = n.recipients
			messagecontent = n.messagecontent
			time_to_send = n.time_to_send
			smsroute = n.smsroute
			scheduleidnum = n.scheduleidnum
			if smsroute == "DND":
				sendwithdnd = APIUrl.objects.filter(is_active=True, api_name__icontains="DND")
				for i in sendwithdnd:
					oto = i.apurl
					apiamtpersms = i.apiamtpersms
					router = "DND ROUTE"
					# print ("send with dnd" + oto )
			else:
				sendwithnotdnd = APIUrl.objects.filter(is_active=True).exclude(api_name__icontains="DND")
				# print(sendwithnotdnd)
				for i in sendwithnotdnd:
					oto = i.apurl
					apiamtpersms = i.apiamtpersms
					router = "NON DND ROUTE"
					# print ("send without dnd" + oto )
			numcount = recipients.split(',')
			numlength = len(numcount)
			totalsms = (len(numcount) * apiamtpersms)
			rt = SmsangoSBulkCredit.objects.get(user=n.user)
			rtcredit = (rt.smscredit)
			if int(totalsms) > int(rt.smscredit):
				successde = "You are low on credit, purchase sms units to send sms" 
				return HttpResponse('Low on Credits')
				#RETREIVE CREDIT FROM DATABASE, SUBTRACT FROM THE MESSAGE SENT AND UPDATE THE DATE BASE BACK WITH THE NEW CREDITS
			else:
				SendScheduledSMS_bg.delay(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, rtcredit, scheduleidnum)
				successde = str(numlength) + " Messages are being sent in background Check <a href='/customer/smshistory'>SMS Report</a> for full details" 
				# context = { "careful": careful, "successdety":successdety, "successde":successde, "lphc":lphc }
				return HttpResponse(successde)
	return HttpResponse ('cron job running')

@login_required(login_url='/customer/login')
def SchedulesmsHistory(request):
	template_name = 'schedule/smshistory.html'
	user = request.user
	get_schedulesmses = SavedScheduledSMS.objects.filter(user=user).order_by('-date')
	paginator = Paginator(get_schedulesmses, 1000)#show 20 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)
	return render(request, template_name, {'historys':historys})


@login_required(login_url='/customer/login')
def SchedulesmsReport(request):
	template_name = 'schedule/smsreport.html'
	queryset = ScheduleSendSMS.objects.filter(user=request.user).order_by('-timestamp')
	paginator = Paginator(queryset, 10)#show 20 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)

	context = {
		"historys": historys
	}
	return render(request, template_name, context)


##Refferal Features
@login_required(login_url='/customer/login')
def RefferalPage(request):
	user = request.user
	template_name = 'refferal.html'
	queryset = UserProfile.objects.filter(refferal=user.username)
	paginator = Paginator(queryset, 10)#show 10 per page
	page = request.GET.get('page')
	try:
		historys = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		historys = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		historys = paginator.page(paginator.num_pages)

	context = {
		"historys": historys
	}
	return render(request, template_name, context)