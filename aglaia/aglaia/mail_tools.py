import json
import datetime
import time

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


def simple_manager_notify_mail(request, **kwargs):
    send_managers_mail(
        True,
        'User Request Submitted',
        'User ' +
        request.user.username +
        ' submitted a request on aglaia. Please handle it as soon as possible.')


def simple_user_notify_mail(request, **kwargs):
    account = None
    if 'account' in kwargs:
        account = kwargs['account']
    elif 'comp' in kwargs:
        account = kwargs['comp'].account
    elif 'borrow' in kwargs:
        account = kwargs['borrow'].account
    else:
        raise Exception('No user found when sending mail to user!')
    if account.email_auth:
        _thread.start_new_thread(
            send_user_mail,
            (account,
             'New changes on your request',
             'Manager ' +
             request.user.username +
             ' changed the status of your request on aglaia. Please check it.'))


def gen_mail_auth_msg(account):
    # Generate a email authetication key and sign to the user. Return the
    # message which will be sent to the user.
    auth_url = EMAIL_AUTH_PREFIX + account.user.username + '/' + account.email_hash + '/'

    message = 'Welcome to AglaiaSys! Please authenticate your email by enter the following address:\n\n\n' + \
        auth_url + '\n\n\nIf you didn\'t sign up on Aglaia, just ignore this email~(^_^)\n'
    return message


def send_auth_email(account):
    # send the email to authenticate the email

    msg = gen_mail_auth_msg(account)
    _thread.start_new_thread(
        send_user_mail, (account, 'Hello! Welcome to Aglaia!', msg))
    return


def send_user_mail(account, subject, message):
    account.user.email_user(subject=subject, message=message)


def send_multi_mails(accounts_list, subject, message):
    for a in accounts_list:
        if a.email_auth:
            send_user_mail(a, subject, message)


def send_managers_mail(use_thread, subject, message):
    ms = Account.objects.filter(user__groups=Group.objects.get(name='manager'))

    # database query before creating thread
    length = len(ms)

    if not use_thread:
        send_multi_mails(ms, subject, message)
    else:
        _thread.start_new_thread(send_multi_mails,
                                 (ms, subject, message))


def send_all_user_mail(subject, message):
    send_multi_mails(Account.objects.all(), subject, message)

# User operation, send mail to managers
CompRequestMail = 0
CompReturnMail = CompRequestMail + 1
CompModfApplyMail = CompReturnMail + 1

# Manager's operation, notify user
CompApproveMail = CompModfApplyMail + 1
CompDisapproveMail = CompApproveMail + 1
CompModfedMail = CompDisapproveMail + 1
CompRejectModfMail = CompModfedMail + 1

# User operation, send mail to managers
BrwRequstMail = CompRejectModfMail + 1
RetRequstMail = BrwRequstMail + 1
MissRequstMail = RetRequstMail + 1
RepairRequstMail = MissRequstMail + 1

# Manager's operation, notify user
AcceptBrwMail = RepairRequstMail + 1
RejectBrwMail = AcceptBrwMail + 1
AcceptRepairMail = RejectBrwMail + 1
RejectRepairMail = AcceptRepairMail + 1
FinishRepairMail = RejectRepairMail + 1

notify_mail_map = {
    # User operation, send mail to managers
    CompRequestMail: simple_manager_notify_mail,
    CompReturnMail: simple_manager_notify_mail,
    CompModfApplyMail: simple_manager_notify_mail,

    # Manager's operation, notify user
    CompApproveMail: simple_user_notify_mail,
    CompDisapproveMail: simple_user_notify_mail,
    CompModfedMail: simple_user_notify_mail,
    CompRejectModfMail: simple_user_notify_mail,

    # User operation, send mail to managers
    BrwRequstMail: simple_manager_notify_mail,
    RetRequstMail: simple_manager_notify_mail,
    MissRequstMail: simple_manager_notify_mail,
    RepairRequstMail: simple_manager_notify_mail,

    # Manager's operation, notify user
    AcceptBrwMail: simple_user_notify_mail,
    RejectBrwMail: simple_user_notify_mail,
    AcceptRepairMail: simple_user_notify_mail,
    RejectRepairMail: simple_user_notify_mail,
    FinishRepairMail: simple_user_notify_mail
}


def send_notify_mail(request, type, **kwargs):
    if SEND_MAIL_NOTIFY:
        try:
            send_mail_func = notify_mail_map[type]
            send_mail_func(request, **kwargs)
        except Exception as e:
            print('send_notify_mail: ', e)
            pass
