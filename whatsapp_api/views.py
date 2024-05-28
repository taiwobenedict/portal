from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

UserModel = get_user_model()

import ast
import json
from decimal import *

import requests
from coreconfig.models import DashboardConfig
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rechargeapp.models import *
from rechargeapp.utility import get_or_none
from smsangonumcredit.views import *
from smsangonumcredit.models import *
from smsangosend.models import SmsangoSBulkCredit

from whatsapp_api.models import *


@csrf_exempt
def generalPostMethod(request):
    app = request.POST.get("app", None)
    get_whatapp_code = WhatsAppSettings.object.all()
    if app is None or (get_whatapp_code.count() > 0 and get_whatapp_code.last().app_code != app):
        return JsonResponse({"reply": "Not allowed"})
    message = request.POST.get("message")
    msg = message.split(" ")
    context = {
        "message": msg,
    }
    if "create" in msg or "reset" in msg:
        hewd = createWhatsappPin(context)
        return JsonResponse({"reply": hewd})
    elif "data" in msg or "airtime" in msg:
        if msg[1].lower() == "data":
            hewd = dataTopKeyword(context, msg[0])
            return JsonResponse({"reply": hewd})
        elif msg[1].lower() == "airtime":
            hewd = airtimeTopUp(context, msg[0])
            return JsonResponse({"reply": hewd})
    return JsonResponse({"reply": "Not processed"})


def airtimeTopUp(context, network):
    """network airtime username amount number_to_load pin"""
    try:
        params = context["message"]
        user = get_or_none(UserModel, username=params[2].strip())
        network = network
        code = network
        phone = params[4]
        amt = params[3]
        pin = params[5]

        if (
            pin.strip() == user.user_whatsapp_access.pin
            and user.user_whatsapp_access.is_active == True
        ):

            # checkApiBalanceAgainstAmt(amt)
            ordernumber = "AT" + get_random_string(length=15)
            smsbal = SmsangoSBulkCredit.objects.get(user=user)
            old_balance = smsbal.smscredit
            bonuscre = BonusAccount.objects.get(user=user)
            # Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
            api_obj = get_or_none(RechargeAirtimeAPI, is_active=True, identifier=code)
            if api_obj == None:
                return render(request, "paystack/failure.html")
            discount = float(api_obj.user_discount)
            ordernumber = "AT" + get_random_string(length=15)
            smsbal = SmsangoSBulkCredit.objects.get(user=user)
            old_balance = smsbal.smscredit
            bonuscre = BonusAccount.objects.get(user=user)
            # Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
            get_amt = float(int(amt) - (float(amt) * (discount)))

            compare = get_amt <= smsbal.smscredit
            if compare is True:
                getApiUrl = api_obj.api_url
                getApiUrlData = api_obj.api_url_data
                network = []
                replace_keys = (
                    ("[phone]", phone),
                    ("[amt]", amt),
                    ("[ordernumber]", ordernumber),
                )
                for (i, j) in replace_keys:
                    getApiUrl = getApiUrl.replace(i, j)
                    getApiUrlData = str(getApiUrlData).replace(i, j)

                # print(getApiUrlData)
                paramet = ast.literal_eval(getApiUrlData)

                print(paramet["data"])

                # Process if User is Reseller
                from resellers.utility import ProcessUserReseller

                is_reseller = ProcessUserReseller(user, float(amt), "airtime", code)

                if is_reseller[1] is True:
                    get_amt = is_reseller[0]
                    print("++>", get_amt)
                print("-->", get_amt)
                smsbal.smscredit -= Decimal(float(get_amt))
                smsbal.save()
                airtime_obj = AirtimeTopup.objects.create(
                    user=user,
                    ordernumber=ordernumber,
                    recharge_amount=float(get_amt),
                    recharge_number=phone,
                    recharge_network=code,
                    status="",  # SUCCESS
                    identifier=code,
                    api_response="",  # info
                    old_balance=float(old_balance),
                    new_balance=float(smsbal.smscredit),
                )

                from vbp_helper import request_method

                info = request_method.call_external_api(
                    getApiUrl, paramet["data"], paramet["headers"]
                )
                print(info)

                if any(respo in str(info) for respo in api_obj.success_code.split(",")):
                    airtime_obj.api_response = info
                    airtime_obj.status = "SUCCESS"
                    airtime_obj.save()

                    if is_reseller[1] is True:
                        bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
                        if not bonus_to_add is None:
                            try:
                                getbonus_amt = GetBonusAmtToCredit(
                                    bonus_to_add,
                                    "purchase_airtime_bonus",
                                    api_obj.identifier,
                                )
                                bonuscre.bonus += Decimal(getbonus_amt * int(amt))
                                bonuscre.save()
                                getrefbonus_percent = GetBonusAmtToCredit(
                                    bonus_to_add,
                                    "referral_airtime_bonus",
                                    api_obj.identifier,
                                )
                                getrefbonus_amt = Decimal(
                                    getrefbonus_percent * int(amt)
                                )
                                CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
                            except:
                                pass
                    return "Airtime Transaction Successful with ID: {}".format(
                        ordernumber
                    )
                else:
                    smsbal.smscredit += Decimal(float(get_amt))
                    smsbal.save()

                    airtime_obj.api_response = info
                    airtime_obj.status = "FAILED"
                    airtime_obj.new_balance = float(smsbal.smscredit)
                    airtime_obj.save()

                    from api_errors.views import ReturnErrorResponse

                    resp = ReturnErrorResponse(
                        info, api_obj.api_name, "Recharge Was Not Successful"
                    )
                    return "Airtime Transaction is not Successful"
            else:
                return "Insufficient Balance"
        else:
            return "Incorrect pin or user has not activated whatsapp usage\nYour Input Pattern should follow\ne.g mtn airtime username amount number pin"
    except Exception as e:
        # raise e
        return "Bad Request Check Your Input Pattern\ne.g mtn airtime username amount number pin"


####### DATA API


def GetTheDataValuesANDSplit(identifier):
    get_active_api = get_or_none(DataNetworks, is_active=True, identifier=identifier)
    oyaSplit = get_active_api.network_data_amount_json.split("|")
    # print(oyaSplit)
    dataNet = {}
    for x in oyaSplit:
        equalToSplit = x.split("=")
        # print(equalToSplit)
        dataNet[equalToSplit[0].lower()] = equalToSplit[1].strip().split(",")
    return dataNet


def GetPrice(data_network, data_size):
    try:
        get_active_api = get_or_none(
            DataNetworks, is_active=True, identifier=data_network
        )
        oyaSplit = get_active_api.network_data_amount_json.split(",")
        # dataSizeSplit = data_size.split("|")
        getNetworkCode, getplancd = {}, {}
        for x in oyaSplit:
            if data_size in x:
                getplancd["otplan_code"] = x
        getOtherParam = getplancd["otplan_code"].split("|")
        # print(getplancd)
        return getOtherParam
    except Exception as e:
        # print(e)
        return "error"


def dataTopKeyword(context, network):
    try:
        params = context["message"]
        user = get_or_none(UserModel, username=params[2].strip())
        pin = params[5]

        if (
            pin.strip() == user.user_whatsapp_access.pin
            and user.user_whatsapp_access.is_active == True
        ):

            data_network = network
            code = network
            data_number = params[4]
            data_size = params[3]
            ordernumber = "w" + data_network[:3] + get_random_string(length=10)

            smsbal = SmsangoSBulkCredit.objects.get(user=user)
            old_balance = smsbal.smscredit
            bonuscre = BonusAccount.objects.get(user=user)
            # Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
            getOtherParam = GetPrice(data_network, data_size)
            apiamount, data_amount, apicode, urlvariable = (
                getOtherParam[0],
                getOtherParam[1],
                getOtherParam[2],
                getOtherParam[3],
            )
            compare = float(data_amount) <= smsbal.smscredit
            # checkApiBalanceAgainstAmt(data_amount)
            if compare is True:
                dataapi = get_or_none(DataNetworks, is_active=True, identifier=code)
                if dataapi == None:
                    return "contact the adminstrator"
                getApiUrl = dataapi.api_url
                getApiUrlData = dataapi.api_url_data
                replace_keys = (
                    ("[network_code]", apicode),
                    ("[phone]", data_number),
                    ("[dataplan]", data_size),
                    ("[apiamount]", apiamount),
                    ("[urlvariable]", urlvariable),
                    ("[network]", data_network),
                )
                for (i, j) in replace_keys:
                    getApiUrl = getApiUrl.replace(i, j)
                    getApiUrlData = str(getApiUrlData).replace(i, j)
                paramet = ast.literal_eval(getApiUrlData)

                from resellers.utility import ProcessUserReseller

                is_reseller = ProcessUserReseller(
                    user, float(data_amount), "data", code, data_size
                )

                if is_reseller[1] is True:
                    data_amount = is_reseller[0]

                smsbal.smscredit -= Decimal(data_amount)
                smsbal.save()
                data_obj = MtnDataShare.objects.create(
                    user=user,
                    ordernumber=ordernumber,
                    data_amount=float(data_amount),
                    dataSize=urlvariable,
                    data_number=data_number,
                    data_network=code,
                    batchno=ordernumber,
                    identifier=code,
                    api_response="",
                    status="",
                    old_balance=float(old_balance),
                    new_balance=float(smsbal.smscredit),
                )

                from vbp_helper import request_method

                info = request_method.call_external_api(
                    getApiUrl, paramet["data"], paramet["headers"]
                )
                print(info)

                print("--->", info)
                if any(respo in str(info) for respo in dataapi.success_code.split(",")):
                    data_obj.api_response = info
                    data_obj.status = "SUCCESS"
                    data_obj.save()

                    if not is_reseller[1]:
                        bonus_to_add = get_or_none(BonusesPercentage, is_active=True)
                        if bonus_to_add is None:
                            pass
                        else:
                            try:
                                getbonus_amt = GetBonusAmtToCredit(
                                    bonus_to_add,
                                    "purchase_data_bonus",
                                    dataapi.identifier,
                                )
                                bonuscre.bonus += Decimal(
                                    getbonus_amt * float(data_amount)
                                )
                                bonuscre.save()
                                getrefbonus_percent = GetBonusAmtToCredit(
                                    bonus_to_add,
                                    "referral_data_bonus",
                                    dataapi.identifier,
                                )
                                getrefbonus_amt = Decimal(
                                    getrefbonus_percent * float(data_amount)
                                )
                                CreditRefferalsOnEveryRecharge(user, getrefbonus_amt)
                            except:
                                pass
                    return "Data Transaction Successful with ID {}".format(ordernumber)
                else:
                    smsbal.smscredit += Decimal(data_amount)
                    smsbal.save()

                    data_obj.api_response = info
                    data_obj.status = "FAILED"
                    data_obj.new_balance = float(smsbal.smscredit)
                    data_obj.save()

                    from api_errors.views import ReturnErrorResponse

                    resp = ReturnErrorResponse(
                        info,
                        dataapi.api_name,
                        "Recharge Was Not Successful \n Try again later",
                    )
                    return "Data Transaction is not Successful"
            else:
                return "Insufficient Balance"
        else:
            return "Incorrect pin or user has not activated whatsapp usage\nYour Input Pattern should follow\ne.g mtn data username datacode number pin"
    except Exception as e:
        # raise e
        return "Bad Request Check Your Input Pattern\ne.g mtn data username data_size number pin"


from coreconfig.models import *


def createWhatsappPin(context):
    params = context["message"]
    try:
        user = get_or_none(UserModel, username=params[1])
        chk_whats_user = get_or_none(WhatsAppPurchaseAccess, user=user)
        if user != None:
            if params[0] == "create":
                if chk_whats_user is None:
                    what_user = WhatsAppPurchaseAccess.objects.create(
                        user=user,
                        pin=get_random_string(length=6, allowed_chars="1234567890"),
                        is_active=True,
                    )
                    return "*{}* \nis your pin\nplease keep but delete from your whatsapp history".format(
                        what_user.pin
                    )
                else:
                    return 'Whatsapp purchase access has been previously created, use your pin to purchase or reset your pin with \n\n"reset username old-pin"'
            elif params[0] == "reset":
                what_user = WhatsAppPurchaseAccess.objects.get(
                    user=user, is_active=True
                )
                if what_user.pin == params[2]:
                    what_user.pin = get_random_string(
                        length=6, allowed_chars="1234567890"
                    )
                    what_user.save()
                    return "*{}* \nis your new pin\nplease keep but delete from your whatsapp history".format(
                        what_user.pin
                    )
                else:
                    return "Pin is incorrect"
        else:
            return "Nothing was done"
    except Exception as e:
        config = DashboardConfig.objects.all()
        if len(config) >= 1:
            return "Something went wrong contact the admin on {}".format(
                config[0].phone
            )
        return "Something went wrong contact the admin"
