from django.dispatch import receiver, Signal
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from smsangosend.models import SmsangoSendSMS, UserProfile, SmsangoSBulkCredit, APIUrl, PhoneBookContacts
from smsangonumcredit.models import PricingPerSMSPerUserToPurchase
from rechargeapp.models import BonusAccount
from django.shortcuts import render, get_object_or_404, redirect
import decimal

sendMailToUser = Signal(providing_args=["user", "subject", "message"])