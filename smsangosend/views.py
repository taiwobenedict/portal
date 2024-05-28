import re, os, requests, datetime, random, string, subprocess
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.core.validators import RegexValidator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.utils.crypto import get_random_string
from django.views import View
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField,
    UserCreationForm,
    PasswordChangeForm,
)
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
from .models import (
    SmsangoSendSMS,
    UserProfile,
    SmsangoSBulkCredit,
    APIUrl,
    PhoneBookContacts,
)
from .utility import *
from smsangonumcredit.models import (
    PricingPerSMSPerUserToPurchase,
    DefaultPricePerSMSToPurchase,
)
from payments.models import *
import decimal
from more_itertools import unique_everseen
from django.contrib import messages
from smsangosend.tasks import send_bulk_sms_bg, SendScheduledSMS_bg
from smsangosend.signals import sendMailToUser
from smsangonumcredit.views import CreditRefferalsOnEveryRecharge
from smsangonumcredit.models import BonusesPercentage
from coreconfig.models import *
from django.conf import settings
from external_cron.views import SMSTask
from rest_framework.authtoken.models import Token
from monnify_app.views import FMonnifyAccountReservation, UpdateAccountReservationBvn

def csrf_failure(request, reason="Form is invalid"):
    messages.error(request, "Form is invalid!")
    return redirect("/")


def signup(request):
    refferal = request.GET.get("refferal")
    if not DashboardConfig.objects.all().exists():
        messages.error(request, "Contact you admin to config his/her site properly")
        return render(
            request,
            "registerpage.html",
            {"register_form": SignUpForm(), "referral": refferal},
        )
    if request.method == "POST":
        phone = (request.POST.get("phone")).strip()
        checkPhone = get_or_none(UserProfile, phone=phone)
        form = SignUpForm(request.POST)
        if checkPhone is not None:
            messages.error(request, "A user with that Phone Number already exist")
            return render(
                request,
                "registerpage.html",
                {"register_form": SignUpForm(), "referral": refferal},
            )
        elif len(phone) < 11 or len(phone) > 13:
            messages.error(request, "Invalid Phone Number")
            return render(
                request,
                "registerpage.html",
                {"register_form": SignUpForm(), "referral": refferal},
            )
        elif UserModel.objects.filter(email=request.POST.get("email")).exists():
            messages.error(request, "Email Already exists")
            return render(
                request,
                "registerpage.html",
                {"register_form": SignUpForm(), "referral": refferal},
            )
        elif UserModel.objects.filter(username=request.POST.get("username")).exists():
            messages.error(request, "Username Already exists")
            return render(
                request,
                "registerpage.html",
                {"register_form": SignUpForm(), "referral": refferal},
            )
        else:
            if form.is_valid():
                user = form.save(commit=False)
                config = DashboardConfig.objects.all()
                if config[0].require_activation == True:
                    user.is_active = False
                else:
                    user.is_active = True
                user.save()
                user.userprofile.refferal = refferal
                user.userprofile.phone = phone
                user.userprofile.save()
                if config[0].allow_payment_for_apikey == False:
                    Token.objects.get_or_create(user=user)
                if config[0].require_activation == True:
                    current_site = get_current_site(request)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    subject = "Activate Your " + config[0].site_name + " Account"
                    message = render_to_string(
                        "account_activation_email.html",
                        {
                            "user": user,
                            "domain": current_site.domain,
                            "uid": uid,
                            "token": account_activation_token.make_token(user),
                        },
                    )
                    sendMailToUser.send(
                        sender=None, user=user, subject=subject, message=message
                    )
                    return redirect("smsangosend:account_activation_sent")
                else:
                    messages.success(request, "Success, you can login now")
                    return redirect("smsangosend:login")
            else:
                errors = form.errors
                form = SignUpForm()
                messages.error(request, errors)
                return render(
                    request,
                    "registerpage.html",
                    {"register_form": form, "referral": refferal},
                )
    else:
        form = SignUpForm()
        return render(
            request, "registerpage.html", {"register_form": form, "referral": refferal}
        )


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
            amt_to_bonus = (
                0 if getbonuspercent is None else getbonuspercent.referral_bonus
            )
            getref.user_bonus.bonus += decimal.Decimal(float(amt_to_bonus))
            getref.user_bonus.save()
            print(getref.user_bonus.bonus)
        except Exception as e:
            pass
        de = SmsangoSBulkCredit.objects.get(user=user)
        getbonuspercent = get_or_none(BonusesPercentage, is_active=True)
        amt_to_bonus = 0 if getbonuspercent is None else getbonuspercent.signup_bonus
        de.smscredit = decimal.Decimal(float(amt_to_bonus))
        de.save()
        current_site = get_current_site(request)
        config = DashboardConfig.objects.all()
        if len(config) == 0:
            subject = "Your VBP Account is Activated"
            message = render_to_string(
                "account_activation_email_followup.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                },
            )
            sendMailToUser.send(
                sender=None, user=user, subject=subject, message=message
            )
        else:
            subject = "Your" + config[0].site_name + "Account is Activated"
            message = render_to_string(
                "account_activation_email_followup.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                },
            )
            sendMailToUser.send(
                sender=None, user=user, subject=subject, message=message
            )
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        return HttpResponseRedirect("/customer/profile-edit")
    else:
        return render(request, "account_activation_invalid.html")


def get_absolute_url(self):
    return reverse("smsangosend:activate")


@login_required(login_url=settings.LOGIN_URL)
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("smsangosend:change_password")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "acc/change_password.html", {"form": form})


@login_required(login_url=settings.LOGIN_URL)
def Home(request):
    return redirect("/customer/")


@login_required(login_url=settings.LOGIN_URL)
def SmsangoSendSMS_createview(request):
    instance = request.user
    user = instance
    userid = int(instance.id)
    if not instance.userprofile.phone:
        messages.success(request, "Update your profile to proceed")
        return HttpResponseRedirect("/customer/profile-edit")
    successde = None
    template_name = "sendsms.html"
    lphc = PhoneBookContacts.objects.filter(user=instance)
    if request.method == "POST":
        form = SmsangoSendSMSForm(request.POST or None)
        if form.is_valid():
            instance = instance
            sender = request.POST.get("sender")
            recipients = request.POST.get("recipients")
            messagecontent = request.POST.get("messagecontent")

            smsroute = request.POST.get("smsroute")
            smsroute = getApiObject(smsroute)
            print(smsroute)
            print(isinstance(smsroute, dict))
            if isinstance(smsroute, dict) is False:
                messages.warning(request, smsroute)
                return redirect("smsangosend:sendsmspage")
            opages = getMsgContent(messagecontent)
            if opages > 3:
                messages.warning(request, "Message content more that 480 characters")
                return redirect("smsangosend:sendsmspage")
            numcount = recipients.split(",")
            numlength = len(numcount)
            if numlength > 100:
                messages.warning(request, "You cant send to more than 100 at once")
                return redirect("smsangosend:sendsmspage")
            totalsms = numlength * smsroute["apiamtpersms"] * opages

            rt = SmsangoSBulkCredit.objects.get(user=instance)
            if int(totalsms) > int(rt.smscredit):
                successde = "You are low on credit, purchase sms units to send sms"
                messages.warning(request, successde)
                return redirect("smsangosend:sendsmspage")
            else:
                send_bulk_sms_bg(userid, sender, recipients, numcount, messagecontent, smsroute, totalsms, opages)
                # SMSTask(
                #     "smsangosend.tasks.send_bulk_sms_bg",
                #     {
                #         "userid": userid,
                #         "sender": sender,
                #         "recipients": recipients,
                #         "numcount": numcount,
                #         "messagecontent": messagecontent,
                #         "smsroute": smsroute,
                #         "totalsms": totalsms,
                #         "opages": opages,
                #     },
                # )
                SmsangoSendSMS.objects.create(
                    user=user,
                    sender=sender,
                    status="QUEUE",
                    recipients=recipients,
                    numcount=len(numcount),
                    messagecontent=messagecontent,
                    smsroute=smsroute,
                    totalsms=totalsms,
                    pages=opages,
                )

                successde = (
                    str(numlength)
                    + " Messages are being sent in background Check <a href='/customer/smshistory'>SMS Report</a> for full details"
                )
                messages.warning(request, successde)
                return redirect("smsangosend:sendsmspage")
    return render(request, template_name, {"lphc": lphc})


@login_required(login_url=settings.LOGIN_URL)
def SmsHistory_listview(request):
    template_name = "smshistory.html"
    queryset = SmsangoSendSMS.objects.filter(user=request.user).order_by("-timestamp")
    paginator = Paginator(queryset, 1000)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)
    return render(
        request,
        template_name,
        {
            "historys": historys,
        },
    )


@login_required(login_url=settings.LOGIN_URL)
def SmsReport_listview(request):
    template_name = "smsreport.html"
    queryset = SmsangoSendSMS.objects.filter(user=request.user).order_by("-timestamp")[
        :10
    ]
    paginator = Paginator(queryset, 1000)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)
    context = {"historys": historys}
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def SmsIndividualReport(request, pk):
    template_name = "smsindireport.html"
    indsmsreport = SmsangoSendSMS.objects.get(
        pk=pk,
        user=request.user,
    )
    context = {"indsmsreport": indsmsreport}
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def Dashboard_View(request):
    template_name = "dashboard.html"
    jonep = request.user

    try:
        UpdateAccountReservationBvn(jonep)
    except:
        FMonnifyAccountReservation(jonep)

    d = SmsangoSBulkCredit.objects.get(user=jonep)
    numb = UserProfile.objects.filter(user=jonep)
    getallreffered = UserProfile.objects.filter(refferal=jonep.username)
    context = {
        "pcredit": d,
        "numb": numb,
        "getallreffered": len(getallreffered),
    }

    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def Phonenumber_view(request):
    template_name = "phone.html"
    if request.method == "POST":
        form = PhoneForm(request.POST or None)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            print(user)
            phone = request.POST.get("phone")
            print(phone)
        instance = UserProfile.objects.get(user=(user))
        instance.phone = form.cleaned_data.get("phone")
        instance.save()
        return HttpResponseRedirect("/customer/")
    return render(request, template_name)


def ExtractNumberwithPrefix(recipien):
    phoneNumRegex = re.compile(r"234\d\d\d\d\d\d\d\d\d\d")
    matches = []
    for i in phoneNumRegex.findall(recipien):
        phoneNum = "".join(
            [
                i[0],
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6],
                i[7],
                i[8],
                i[9],
                i[10],
                i[11],
                i[12],
            ]
        )
        matches.append(phoneNum)
    processrecipients = ",\n".join(matches)
    return processrecipients.strip()


def RemovePrefix(recipien):
    phoneNumRegex = re.compile(r"\b234")
    recipients = phoneNumRegex.sub(r"0", recipien, count=0)
    phoneNumRegex = re.compile(r"0\d\d\d\d\d\d\d\d\d\d")
    matches = []
    for i in phoneNumRegex.findall(recipients):
        phoneNum = "".join(
            [i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10]]
        )
        matches.append(phoneNum)
    processrecipients = ",\n".join(matches)
    return processrecipients.strip()


def substitut(recipien):
    phoneNumRegex = re.compile(r"\b0")
    recipients = phoneNumRegex.sub(r"234", recipien, count=0)
    phoneNumRegex = re.compile(r"234\d\d\d\d\d\d\d\d\d\d")
    matches = []
    for i in phoneNumRegex.findall(recipients):
        phoneNum = "".join(
            [
                i[0],
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6],
                i[7],
                i[8],
                i[9],
                i[10],
                i[11],
                i[12],
            ]
        )
        matches.append(phoneNum)
    processrecipients = ",\n".join(matches)
    return processrecipients.strip()


def Removeduplicate(recipien):
    match = list(unique_everseen(recipien))
    matches = []
    for i in match:
        matches.append(i)
    processrecipients = ",".join(matches)
    return processrecipients.strip()


@login_required(login_url=settings.LOGIN_URL)
def Phonenumberextractor(request):
    instance = request.user
    if not instance.userprofile.phone:
        messages.success(request, "Update your profile to proceed")
        return HttpResponseRedirect("/customer/profile-edit")
    template_name = "phonenumberextrator.html"
    if request.method == "POST":
        recipients = request.POST.get("recipients")
        operations = request.POST.get("operations")
        if operations == "Addprefix":
            phoneextracted = substitut(recipients)
            lent = phoneextracted.split(",")
            processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
        elif operations == "extractwithprefix":
            phoneextracted = ExtractNumberwithPrefix(recipients)
            lent = phoneextracted.split(",")
            processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
        elif operations == "Removeprefix":
            phoneextracted = RemovePrefix(recipients)
            lent = phoneextracted.split(",")
            processed = str(len(lent)) + " NUMBERS WAS PROCESSED"
        elif operations == "Removeduplicate":
            recip = recipients.split(",")
            print(recip)
            phoneextracted = Removeduplicate(recip)
            lent = phoneextracted.split(",")
            processed = str(len(lent)) + " NUMBERS WAS PROCESSED! DUPLICATES REMOVED"
        else:
            processed = "SOMETHING WENT WRONG"
        context = {
            "recipients": recipients,
            "phoneextracted": phoneextracted,
            "processed": processed,
        }
        template_name = "phonenumberextrator.html"
        return render(request, template_name, context)
    return render(request, template_name)


@login_required(login_url=settings.LOGIN_URL)
def PhoneBookContactsView(request):
    template_name = "phonebookcontact.html"
    instance = request.user
    if not instance.userprofile.phone:
        messages.success(request, "Update your profile to proceed")
        return HttpResponseRedirect("/customer/profile-edit")
    phc = PhoneBookContacts.objects.filter(user=instance)
    idname = []
    name = []
    counted_contacts = []
    for j in phc:
        aj = j.name_contacts
        idj = j.id
        cn = j.contact_numbers
        cox = cn.split(",")
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
            uploadedfile = request.FILES.get("uploadcontacts", "")
            if uploadedfile:
                try:
                    if not uploadedfile.name.endswith(".txt"):
                        messages.error(request, "Upload .txt file please")
                        return redirect("smsangosend:phonebooks")
                    elif uploadedfile.multiple_chunks():
                        messages.error(
                            request,
                            "Uploaded file is too big (%.2f MB)."
                            % (uploadedfile.size / (1000 * 1000),),
                        )
                        return redirect("smsangosend:phonebooks")
                    else:
                        uplod = uploadedfile.read().decode("utf-8")
                        uplos = uplod.strip()
                        print(uplos)
                        PhoneBookContacts.objects.create(
                            user=(instance),
                            contact_numbers=uplos,
                            name_contacts=name_contacts,
                        )
                        messages.success(request, "Contacts successfully saved")
                        return redirect("smsangosend:phonebooks")
                except:
                    pass
            elif contact_numbers:
                obj = PhoneBookContacts.objects.create(
                    user=(instance),
                    contact_numbers=contact_numbers,
                    name_contacts=name_contacts,
                )
                messages.success(request, "Contacts successfully saved")
                return redirect("smsangosend:phonebooks")
    else:
        form = PhoneBookContactsForm()
        context = {
            "form": form,
            "phc": phc,
            "phk": zip(name, counted_contacts, idname),
        }
        return render(request, template_name, context)
    return render(request, template_name)


@login_required(login_url=settings.LOGIN_URL)
def PhoneBookContactsViewEdit(request, pk):
    number_instance = get_object_or_404(PhoneBookContacts, pk=pk)
    if request.method == "POST":
        edit_contact_form = PhoneBookContactsEditForm(request.POST or None)
        if edit_contact_form.is_valid():
            name_contacts = request.POST.get("name_contacts")
            contact_numbers = request.POST.get("contact_numbers")
            obj, created = PhoneBookContacts.objects.update_or_create(
                pk=pk,
                user=request.user,
                defaults={
                    "name_contacts": name_contacts,
                    "contact_numbers": contact_numbers,
                },
            )
            messages.success(request, "Contacts Updated!")
            return redirect("smsangosend:phonebooks")
        else:
            messages.error(request, "Please correct the error below.")
    return render(
        request,
        "edits/edit_contact_form.html",
        {
            "name": number_instance.name_contacts,
            "numbers": number_instance.contact_numbers,
        },
    )


@login_required(login_url=settings.LOGIN_URL)
def Contact_Delete(request, pk, template_name="edits/contacts_confirm_delete.html"):
    delcontact = get_object_or_404(PhoneBookContacts, pk=pk)
    if request.method == "POST":
        delcontact.delete()
        return redirect("smsangosend:phonebooks")
    return render(request, template_name, {"delcontact": delcontact})


@login_required(login_url=settings.LOGIN_URL)
def LoadNumbersFromSelectedList(request):
    getphoneid = request.GET.get("phonebook", None)
    phcnumber = PhoneBookContacts.objects.get(id=int(getphoneid))
    return render(request, "partials/dropdown_option.html", {"phcnumber": phcnumber})


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


@login_required(login_url=settings.LOGIN_URL)
def FisrtPriceChoicePlan(request):
    template_name = "paystack/select_plan.html"
    return render(request, template_name, {})


@login_required(login_url=settings.LOGIN_URL)
def PriceChoicePlan(request):
    # IMPORT RESELLER PACKAGE
    from resellers.utility import IsReseller, ProcessUserReseller

    template_name = "paystack/payment_page.html"
    user = request.user

    is_reseller = IsReseller(user)

    if not user.userprofile.phone:
        return HttpResponseRedirect("/customer/profile-edit")
    if request.method == "POST":
        amounttobuy = request.POST.get("amounttobuy")
        orderid = random_string_generator(size=20)

        # CHECK IF USER IS A RESELLER
        if is_reseller[1] is True:
            get_min_fund = is_reseller[0][1]
            if int(amounttobuy) < get_min_fund.fund_to_wallet:
                messages.error(
                    request,
                    "The minimum a {0} Reseller can fund into your wallet is NGN {1}".format(
                        get_min_fund.name, get_min_fund.fund_to_wallet
                    ),
                )
                return redirect("smsangosend:toenteramount")
        else:
            pass

        dash = DashboardConfig.objects.all()[0]
        if int(amounttobuy) > dash.amount_funding_limit_through_paysatack:
            messages.error(
                request,
                "The highest Amount you can pay once is {} per transaction".format(
                    dash.amount_funding_limit_through_paysatack
                ),
            )
            return redirect("smsangosend:toenteramount")
        else:
            try:
                getuserspecificprice = PricingPerSMSPerUserToPurchase.objects.get(
                    user=user
                )
                cedituser = getuserspecificprice.price
                context = {
                    "getuserspecificprice": cedituser,
                    "amounttobuy": (
                        (float(amounttobuy) * float(dash.amount_funding_percentage))
                        + float(amounttobuy)
                    )
                    * 100,
                    "amounttobuyy": (
                        (float(amounttobuy) * float(dash.amount_funding_percentage))
                        + float(amounttobuy)
                    ),
                    "orderid": orderid,
                    "realamounttobuy": amounttobuy,
                }
                return render(request, template_name, context)
            except ObjectDoesNotExist:
                getdefaultprice = DefaultPricePerSMSToPurchase.objects.filter(
                    is_active=True
                )
                getdefaultprice = getdefaultprice.first().priceperunit if getdefaultprice.exists() else 1

                context = {
                    "getuserspecificprice": float(getdefaultprice),
                    "amounttobuy": (
                        (float(amounttobuy) * float(dash.amount_funding_percentage))
                        + float(amounttobuy)
                    )
                    * 100,
                    "amounttobuyy": (
                        (float(amounttobuy) * float(dash.amount_funding_percentage))
                        + float(amounttobuy)
                    ),
                    "orderid": orderid,
                    "realamounttobuy": amounttobuy,
                }
                return render(request, template_name, context)
        return render(request, template_name)
    return render(request, template_name)


from .tokens import TokenAuth
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


def PaystackSuccess(request):
    amountfrompayst = request.session["amount"]
    updatesmscredit = request.session["newbalance"]
    reference = request.session["reference"]
    template_name = "paystack/success_page.html"
    context = {
        "amountfrompayst": amountfrompayst,
        "reference": reference,
        "updatesmscredit": updatesmscredit,
    }
    return render(request, template_name, context)


def PaystackFailure(request):
    template_name = "paystack/failure.html"
    return render(request, template_name, {})


@login_required(login_url=settings.LOGIN_URL)
def PaystackCallBack(request):
    usertocredit = request.user
    userid = request.POST["id"]
    orderid = request.POST["trxref"]
    reference = request.POST["reference"]
    amount = request.POST["amount"]
    price = request.POST["price"]
    realamounttobuy = request.POST["realamount"]
    url = "https://api.paystack.co/transaction/verify/{}".format(reference)
    r = requests.get(
        url, auth=TokenAuth(DashboardConfig.objects.all()[0].paystack_sk_token)
    )
    print(r.content)
    response = json.loads(r.text)
    if (
        int(usertocredit.id) == int(userid)
        and response["data"]["status"] == "success"
        and float(amount) == float(response["data"]["amount"])
    ):
        amountfrompayst = float(realamounttobuy) / 100
        amtcredited = round((float(realamounttobuy) / float(price)), 2)
        get_user = SmsangoSBulkCredit.objects.get(user=usertocredit)
        old_balance = get_user.smscredit
        objpay = PayStackPayment.objects.create(
            user=usertocredit,
            smsangosbulkcredit=get_user,
            order_id=orderid,
            amtcredited=amtcredited,
            amount=realamounttobuy,
            old_balance=float(old_balance),
            new_balance=float(get_user.smscredit),
            reference=reference,
        )

        updatesmscredit = float(get_user.smscredit) + float(amtcredited)
        get_user.smscredit = updatesmscredit
        get_user.save()

        objpay.new_balance = get_user.smscredit
        objpay.save()

        request.session["amount"] = realamounttobuy
        request.session["newbalance"] = updatesmscredit
        request.session["reference"] = reference
        context = {
            "status": response["data"]["status"],
            "orderid": orderid,
            "amount": realamounttobuy,
            "amtotcredit": realamounttobuy,
            "updatesmscredit": updatesmscredit,
        }
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({"error": "failed"}, safe=False)
    return JsonResponse({"error": "failed"}, safe=False)


@login_required(login_url=settings.LOGIN_URL)
def PaymentHistory(request):
    user = request.user
    userpay_history = PayStackPayment.objects.filter(user=user).order_by("-dated")
    paginator = Paginator(userpay_history, 1000)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)

    context = {"historys": historys}
    return render(request, "paystack/payment_history.html", context)


@login_required(login_url=settings.LOGIN_URL)
def UserProfileUpdates(request):
    user = request.user
    get_profile = UserProfile.objects.get(user=user)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=user.userprofile
        )
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
    template_name = "profile.html"
    return render(
        request,
        template_name,
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "get_profile": get_profile,
        },
    )


import pytz

utc = pytz.UTC


@login_required(login_url=settings.LOGIN_URL)
def SavedScheduleSMS(request):
    template_name = "schedule/schedulesms.html"
    user = request.user
    if not user.userprofile.phone:
        return HttpResponseRedirect("smsangosend:profile_edit")
    lphc = PhoneBookContacts.objects.filter(user=user)
    if request.method == "POST":
        sender = request.POST.get("sender")
        recipients = request.POST.get("recipients")
        messagecontent = request.POST.get("messagecontent")
        time_to_send = request.POST.get("time_to_send")
        smsroute = request.POST.get("smsroute")
        print(sender, recipients, messagecontent, time_to_send, smsroute)
        smsrouter = getApiObject(smsroute)
        if isinstance(smsrouter, dict) is False:
            messages.warning(request, smsrouter)
            return redirect("smsangosend:savedschedulesms")
        opages = getMsgContent(messagecontent)
        if opages > 3:
            messages.warning(request, "Message content more that 480 characters")
            return redirect("smsangosend:savedschedulesms")
        numcount = recipients.split(",")
        numlength = len(numcount)
        if numlength > 100:
            messages.warning(request, "You cant send to more than 100 at once")
            return redirect("smsangosend:savedschedulesms")
        totalsms = numlength * smsrouter["apiamtpersms"] * opages
        rt = SmsangoSBulkCredit.objects.get(user=user)
        if int(totalsms) > int(rt.smscredit):
            successde = "You are low on credit, purchase sms units to send sms"
            messages.warning(request, successde)
            return redirect("smsangosend:savedschedulesms")
        else:
            print("inside the if condition")
            datetime_obj = datetime.datetime.strptime(time_to_send, "%Y-%m-%d %H:%M:%S")
            datetime_obj_utc = datetime_obj.replace(tzinfo=utc)
            print(datetime_obj_utc)
            obj = SavedScheduledSMS.objects.create(
                user=user,
                sender=sender,
                recipients=recipients,
                messagecontent=messagecontent,
                time_to_send=datetime_obj_utc,
                smsroute=smsroute,
                scheduleidnum=get_random_string(length=14),
            )
            time_to_sendd = obj.time_to_send
            successde = "SMS has been scheduled to sent at exactly " + str(
                time_to_sendd
            )
            messages.warning(request, successde)
            return redirect("smsangosend:savedschedulesms")
    else:
        return render(request, template_name, {"lphc": lphc})
    return render(request, template_name, {"lphc": lphc})


def SchedulingSMS(request):
    successde = None
    timenow = timezone.now()
    difftime = datetime.timedelta(minutes=60)
    futuretime = timenow + difftime
    get_schedulemsg = SavedScheduledSMS.objects.filter(
        time_to_send__gte=timenow, status=False
    )
    for n in get_schedulemsg:
        userid = n.user.id
        instance = n.user
        if n.time_to_send >= timenow and n.time_to_send <= futuretime:
            print(n)
            sender = n.sender
            recipients = n.recipients
            messagecontent = n.messagecontent
            time_to_send = n.time_to_send
            smsroute = n.smsroute
            scheduleidnum = n.scheduleidnum
            smsroute = getApiObject(smsroute)
            print(smsroute)
            print(isinstance(smsroute, dict))

            opages = getMsgContent(messagecontent)

            numcount = recipients.split(",")
            numlength = len(numcount)

            totalsms = numlength * smsroute["apiamtpersms"] * opages
            print("Amount to Deduct ==> ", totalsms)
            rt = SmsangoSBulkCredit.objects.get(user=instance)
            rtcredit = rt.smscredit
            if (
                isinstance(smsroute, dict) is False
                or opages > 3
                or int(totalsms) > int(rt.smscredit)
                or numlength > 100
            ):
                continue
            else:
                SendScheduledSMS_bg(
                    userid,
                    sender,
                    recipients,
                    numcount,
                    messagecontent,
                    smsroute,
                    totalsms,
                    rtcredit,
                    scheduleidnum,
                    opages,
                )
    return HttpResponse("cron job running")


@login_required(login_url=settings.LOGIN_URL)
def SmsIndividualReportSched(request, schedule):
    template_name = "smsindireport.html"
    indsmsreport = ScheduleSendSMS.objects.get(
        scheduleidnum=schedule, user=request.user
    )
    context = {"indsmsreport": indsmsreport}
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def SchedulesmsHistory(request):
    template_name = "schedule/smshistory.html"
    user = request.user
    get_schedulesmses = SavedScheduledSMS.objects.filter(user=user).order_by("-date")
    paginator = Paginator(get_schedulesmses, 1000)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)
    return render(request, template_name, {"historys": historys})


@login_required(login_url=settings.LOGIN_URL)
def SchedulesmsReport(request):
    template_name = "schedule/smsreport.html"
    queryset = ScheduleSendSMS.objects.filter(user=request.user).order_by("-timestamp")
    paginator = Paginator(queryset, 10)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)

    context = {"historys": historys}
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def RefferalPage(request):
    user = request.user
    template_name = "refferal.html"
    queryset = UserProfile.objects.filter(refferal=user.username)
    paginator = Paginator(queryset, 10)
    page = request.GET.get("page")
    try:
        historys = paginator.page(page)
    except PageNotAnInteger:
        historys = paginator.page(1)
    except EmptyPage:
        historys = paginator.page(paginator.num_pages)

    context = {"historys": historys}
    return render(request, template_name, context)


from django.core.management import call_command
import sys


def DBBackUp(request):
    with open(os.path.join(os.getcwd(), "dbbk.json"), "w") as f:
        call_command("dumpdata", exclude=["contenttypes", "auth"], stdout=f)
    return HttpResponse("Run Cron Jobs")


def RunCronJobForSMS(request):
    process = subprocess.call(
        [sys.executable, "manage.py", "process_tasks --duration 10000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # print(subprocess.Popen().communicate)
    # stdout, stderr = process.communicate()
    print(process)
    print(sys.executable)
    # print(stderr)
    return HttpResponse("Run Cron Jobs")
