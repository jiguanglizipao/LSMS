from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required

from aglaia.settings import LOGIN_URL, ACCOUNT_HOME_URL, EMAIL_AUTH_PREFIX, USER_RETURN_MESSAGE, USER_MISS_MESSAGE
from aglaia.views import show_message, get_context_list, no_excp_post, no_excp_get
from aglaia.decorators import permission_required, method_required, http_denied, show_denied_message
from aglaia.messages import *
from account.views import get_context_user
from account.models import *
from goods.models import *
from account.interface import *
from computing.interface import *
from goods.interface import *
from aglaia.mail_tools import *

from computing.views import get_context_computing, get_context_pack
import json

from aglaia.message_center import Message
from django.core.management import execute_from_command_line
import os
import sys
import time
from django import forms
import hashlib
import xlrd
import xlwt


class UploadFileForm(forms.Form):
    file = forms.FileField()


def handle_uploaded_file(request, f):
    destination = open('excel/tmp.xml', 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def make_hash(data):
    md5 = hashlib.md5(data.encode('utf-8')).hexdigest()
    return md5


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def export_database(request):
    execute_from_command_line(['manage.py', 'dumpdata', '--output', 'excel/tmp.xml', '--format', 'xml', '--indent', '4'])
    file = open('excel/tmp.xml')
    data = file.read()
    file.close()
    data = make_hash(data)+'\n'+data
    filename = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+'.xml'
    response = StreamingHttpResponse(data)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename='+filename
    os.remove('excel/tmp.xml')
    return response


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def import_database(request):
    file = open('excel/tmp.xml')
    hash = file.readline().replace('\n', '')
    data = file.read()
    file.close()
    os.remove('excel/tmp.xml')
    if hash != make_hash(data):
        return show_message(request, 'Import Error')
    file = open('excel/tmp.xml', 'w')
    file.write(data)
    file.close()
    execute_from_command_line(['manage.py', 'loaddata', 'excel/tmp.xml'])
    os.remove('excel/tmp.xml')
    return show_message(request, 'Import Success')


@permission_required(PERM_GOODS_AUTH)
def index(request):
    if request.method == 'GET':
        return render(request, "excel_index.html", {
            'user': get_context_user(request.user),
            'perm_list': request.user.get_all_permissions()})

    if 'file' in request.FILES:
        handle_uploaded_file(request, request.FILES['file'])
        return HttpResponseRedirect('import_database')
    else:
        return HttpResponseRedirect('')


def export_excel(request):
    workbook = xlwt.Workbook('utf-8')
    workbook.set_owner('LSMS')
    workbook.set_country_code(86)

    sheet = workbook.add_sheet('在库物品')
    sheet.write(0, 0, 'SN号')
    sheet.write(0, 1, '物品种类')
    sheet.write_merge(0, 0, 2, 128, '物品属性')
    singles = Single.objects.all().filter(status=AVALIABLE_KEY)

    i = 1
    for item in singles:
        sheet.write(i, 0, item.sn)
        sheet.write(i, 1, item.goods.gtype.name)
        pro_names = item.goods.gtype.pro_names
        pro_names = pro_names.split(',')
        pro_values = item.goods.pro_values
        pro_values = pro_values.split(sep)
        j = 0
        for pro in pro_names:
            if not pro:
                continue
            sheet.write(i, 2+j, pro+" : "+pro_values[j])
            j += 1
        i += 1

    workbook.save('tmp.xls')
    return show_message(request, '123')
