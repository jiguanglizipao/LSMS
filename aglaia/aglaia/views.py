from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================


def show_message(request, msg):
    return render(request, "message.html", {'message': msg})


def get_context_list(obj_list, func):
    l = []
    for obj in obj_list:
        l.append(func(obj))
    return l


def no_excp_post(request, key, default=""):
    """Get the value to a key in request.POST.

    If the key does not exist, return empty string."""
    retval = default
    try:
        retval = request.POST[key]
    except KeyError:
        pass
    return retval


def no_excp_get(request, key, default=None):
    """ Helper function to access request.GET[key]"""
    retval = default
    try:
        retval = request.GET[key]
    except KeyError:
        pass
    return retval
