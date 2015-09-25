
from django.http import Http404, HttpResponseRedirect, HttpResponse

from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required

from aglaia.settings import LOGIN_URL, ACCOUNT_HOME_URL, EMAIL_AUTH_PREFIX
from account.models import *
from account.interface import *
from aglaia.views import show_message

import json

def show_denied_message(request, *args, **kwargs):
    return show_message(request, "Permission denied!")

def http_denied(request, *args, **kwargs):
    return HttpResponse('denied')

def json_denied(request, *args, **kwargs):
    return HttpResponse(json.dumps({'retcode':'denied'}))

def permission_required(perm, denied_func=show_denied_message):
    def perm_wrap(func):

        @login_required
        def wrap_func(request, *args, **kwargs):
            if request.user.has_perm(perm) and request.user.is_active:
                return func(request, *args, **kwargs)
            return denied_func(request, *args, **kwargs)
        return wrap_func
    return perm_wrap

def method_required(mthd):
    def mthd_wrap(func):
        def wrap_func(request, *args, **kwargs):
            if not request.method == mthd:
                raise Http404
            return func(request, *args, **kwargs)
        return wrap_func
    return mthd_wrap
