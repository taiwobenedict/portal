from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from smsangosend.models import *
from rechargeapp.models import BonusAccount, RefBonusAccount
import decimal
from coreconfig.models import DashboardConfig
from smsangosend.signals import sendMailToUser
import json

def get_or_none(Model, **kwarg):
    try:
        obj = Model.objects.get(**kwarg)
        return obj
    except ObjectDoesNotExist:
        return None


def GetBonusAmtToCredit(bonus_to_add, service, identifier):
    try:
        get_json_amount = getattr(bonus_to_add, service)
        the_json = json.loads(get_json_amount) 
        get_amt = the_json[identifier]
        return float(get_amt)
    except Exception as e:
        return 0
    return 0

# Methods for Rewarding Refferal On Every recharge there downline brings
def CreditRefferalsOnEveryRecharge(user, amt):
    print(user.username, user.userprofile.phone, amt)
    try:
        getTheRef = get_or_none(UserProfile, user=user)
        print("===>", getTheRef)
        if getTheRef != None:
            getuserref = getTheRef.refferal
            print(getuserref, "referral is")
            from django.contrib.auth.models import User
            getusertocredit = User.objects.get(username=getuserref)
            getuserbonusacc = BonusAccount.objects.get(user=getusertocredit)
            getuserbonusacc.oldbonus = getuserbonusacc.bonus
            getuserbonusacc.bonus += decimal.Decimal(amt)
            print("inside the credit referal")
            getuserbonusacc.save()
            refgetuserbonusacc = RefBonusAccount.objects.create(
                user=getusertocredit,
                refbonus = getuserbonusacc.bonus,
                refoldbonus = getuserbonusacc.oldbonus,
                redeemed = '',
                )
            refgetuserbonusacc.save()
            config = DashboardConfig.objects.all()
            if len(config) == 0:
                pass
            else:
                subject = config[0].site_name + 'Earning Notification'
                message = render_to_string('bonus/bonus_notifications.html', { 
                        'username':getusertocredit.username, 'bonuscre': amt, 'bonusamount':getuserbonusacc.bonus
                        })
                sendMailToUser.send(sender=None, user=getusertocredit, subject=subject, message=message)
                return ('Done')
    except Exception as e:
        # raise e
        return ('Invalid')

def RedeemBonusToOcCredits(user):
    try:
        getuser = user
        getsmscredit = SmsangoSBulkCredit.objects.get(user=getuser)
        getuserbonus = BonusAccount.objects.get(user=getuser)
        oldbonus = getuserbonus.bonus
        getsmscredit.smscredit += getuserbonus.bonus
        getsmscredit.save()
        getuserbonus.bonus = decimal.Decimal(0)
        getuserbonus.save()
        getuserbonusaccc = BonusAccount.objects.get(user=getuser)
        refgetuserbonusacc = RefBonusAccount.objects.create(
            user=getuser,
            refbonus = getuserbonusaccc.bonus,
            refoldbonus = oldbonus,
            redeemed = 'Bonus Redeemed',
            )
        refgetuserbonusacc.save()
        config = DashboardConfig.objects.all()
        if len(config) == 0:
            pass
        else:
            subject = config[0].site_name + 'Earning Notification'
            message = render_to_string('bonus/bonus_notifications.html', { 
                    'username':getuser.username, 'oldbonus': oldbonus
                    })
            sendMailToUser.send(sender=None, user=getuser, subject=subject, message=message)

            return ('Done')
    except Exception as e:
        # print (e)
        # print('something wenet terribly wrong')
        return ('invalid')

def DotheRedeemNow(request):
    template_name = ''
    user = request.user
    redim = RedeemBonusToOcCredits(user)
    print(redim)
    if redim == 'Done':
        messages.success(request, 'Congrats Your Bonus was Successfully Redeemed')
        return redirect ('smsangosend:customer')
    else:
        messages.success(request, 'Nothing Happened')
        return redirect ('smsangosend:customer')
    return redirect ('smsangosend:customer')

def BonusHistory(request):
    template_name = 'bonus/bonus.html'
    user = request.user
    try:
        bonushistory = RefBonusAccount.objects.filter(user=user).order_by('-updated_date')
        # print(bonushistory)
        paginator = Paginator(bonushistory, 10)#show 10 per page
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
    except Exception as e:
        context = {
            "historys": ''
        }
        return render(request, template_name, context)
