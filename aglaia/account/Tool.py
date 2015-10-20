__author__ = 'Somefive'

import json, datetime, time

from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required

from aglaia.settings import LOGIN_URL, ACCOUNT_HOME_URL, EMAIL_AUTH_PREFIX, SEND_MAIL_NOTIFY
from aglaia.decorators import *
from aglaia.views import show_message, get_context_list, no_excp_post, no_excp_get
from aglaia.messages import *

from account.views import *
from account.models import *
from computing.models import *
from goods.models import *
import _thread
from account.interface import *

def SpeakMessage(sender_name,receiver_name,words):
    try:
        sender = Account.objects.get(user__username=sender_name)
        receiver = Account.objects.get(user__username=receiver_name)
    except:
        raise UserDoesNotExistError("Invalid Name")
    sender.messages = str(sender.messages) + "&" + sender_name + ":" + words
    receiver.messages = str(receiver.messages) + "&" + sender_name + ":" + words
    pass

#def SpeakToAllManager(sender_name,words):
#    managers = Account.objects.filter(user__groups=Group.objects.get(name='manager'))
#