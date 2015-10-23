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
import io
from random import Random


class UploadFileForm(forms.Form):
    file = forms.FileField()


def random_str(randomlength=8):
    ran = str()
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        ran += chars[random.randint(0, length)]
    return ran


def handle_uploaded_file(request, f):
    ran = random_str()
    destination = open('excel/'+ran+'.xml', 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return ran


def make_hash(data):
    md5 = hashlib.md5(data.encode('utf-8')).hexdigest()
    return md5


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def export_database(request):
    ran = 'excel/'+random_str()+'.xml'
    execute_from_command_line(['manage.py', 'dumpdata', '--output', ran, '--format', 'xml', '--indent', '4'])
    file = open(ran)
    data = file.read()
    file.close()
    data = make_hash(data)+'\n'+data
    filename = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+'.xml'
    response = StreamingHttpResponse(data)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename='+filename
    os.remove(ran)
    return response


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def import_database(request):
    ran = 'excel/'+request.GET['ran']+'.xml'
    file = open(ran)
    hash = file.readline().replace('\n', '')
    data = file.read()
    file.close()
    os.remove(ran)
    if hash != make_hash(data):
        return show_message(request, 'Import Error')
    file = open(ran, 'w')
    file.write(data)
    file.close()
    execute_from_command_line(['manage.py', 'loaddata', ran])
    os.remove(ran)
    return show_message(request, 'Import Success')


@permission_required(PERM_GOODS_AUTH)
def index(request):
    if request.method == 'GET':
        return render(request, "excel_index.html", {
            'user': get_context_user(request.user),
            'perm_list': request.user.get_all_permissions()})

    if 'file' in request.FILES:
        ran = handle_uploaded_file(request, request.FILES['file'])
        return HttpResponseRedirect('import_database?ran='+ran)
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

    sheet = workbook.add_sheet('借出物品')
    sheet.write(0, 0, 'SN号')
    sheet.write(0, 1, '借用者')
    sheet.write(0, 2, '借用状态')
    sheet.write(0, 3, '物品种类')
    sheet.write_merge(0, 0, 4, 128, '物品属性')
    singles = Single.objects.all()
    singles = singles.exclude(status=AVALIABLE_KEY)
    singles = singles.exclude(status=DESTROYED_KEY)
    singles = singles.exclude(status=LOST_KEY)

    i = 1
    for item in singles:
        sheet.write(i, 0, item.sn)
        sheet.write(i, 1, item.user_name)
        sheet.write(i, 2, item.get_status_display())
        sheet.write(i, 3, item.goods.gtype.name)
        pro_names = item.goods.gtype.pro_names
        pro_names = pro_names.split(',')
        pro_values = item.goods.pro_values
        pro_values = pro_values.split(sep)
        j = 0
        for pro in pro_names:
            if not pro:
                continue
            sheet.write(i, 4+j, pro+" : "+pro_values[j])
            j += 1
        i += 1

    sheet = workbook.add_sheet('申请物资')
    sheet.write(0, 0, '物品名')
    sheet.write(0, 1, 'SN号')
    sheet.write(0, 2, '申请者')
    sheet.write(0, 3, '申请状态')
    sheet.write(0, 4, '物品种类')
    sheet.write_merge(0, 0, 5, 128, '物品属性')
    singles = Apply_Goods.objects.all()
    singles = singles.exclude(status=FINISH_GOODS_APPLY_KEY)
    singles = singles.exclude(status=INPUT_GOODS_APPLY_KEY)

    i = 1
    for item in singles:
        sheet.write(i, 0, item.name)
        sheet.write(i, 1, item.sn)
        sheet.write(i, 2, item.account.user.username)
        sheet.write(i, 3, item.get_status_display())
        sheet.write(i, 4, item.type_name)
        pro_names = item.pro_names
        pro_names = pro_names.split(sep)
        pro_values = item.pro_values
        pro_values = pro_values.split(sep)
        j = 0
        for pro in pro_names:
            if not pro:
                continue
            sheet.write(i, 5+j, pro+" : "+pro_values[j])
            j += 1
        i += 1

    sheet = workbook.add_sheet('计算资源')
    sheet.write(0, 0, '资源名')
    sheet.write(0, 1, 'SN号')
    sheet.write(0, 2, '借用者')
    sheet.write(0, 3, '借用状态')
    sheet.write(0, 4, '套餐名')
    sheet.write(0, 5, '资源种类')
    sheet.write(0, 6, 'CPU种类')
    sheet.write(0, 7, '内存大小')
    sheet.write(0, 8, '硬盘种类')
    sheet.write(0, 9, '硬盘大小')
    sheet.write(0, 10, '操作系统')
    sheet.write(0, 11, '期满时间')
    sheet.write(0, 12, '用户名')
    sheet.write(0, 13, '密码')
    sheet.write(0, 14, 'IP')
    sheet.write(0, 15, '是否有重要数据')
    sheet.write(0, 16, '重要数据内容')

    singles = Computing.objects.all()
    singles = singles.exclude(status=DESTROYED_KEY)
    singles = singles.exclude(status=DAMAGED_KEY)

    i = 1
    for item in singles:
        sheet.write(i, 0, item.name)
        sheet.write(i, 1, item.sn)
        sheet.write(i, 2, item.account.user.username)
        sheet.write(i, 3, item.get_status_display())
        dic={PHYSICAL_MACHINE_KEY: '实体机', VIRTUAL_MACHINE_KEY:'虚拟机'}
        sheet.write(i, 4, item.pack_name)
        sheet.write(i, 5, dic[item.pc_type])
        sheet.write(i, 6, item.cpu)
        sheet.write(i, 7, item.memory)
        sheet.write(i, 8, item.get_disk_type_display())
        sheet.write(i, 9, item.disk)
        sheet.write(i, 10, item.os)
        sheet.write(i, 11, str(item.expire_time))
        sheet.write(i, 12, item.login)
        sheet.write(i, 13, item.password)
        sheet.write(i, 14, item.address)
        sheet.write(i, 15, str(item.flag))
        sheet.write(i, 16, item.data_content)
        i += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    filename = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+'.xls'
    response['Content-Disposition'] = 'attachment; filename='+filename
    workbook.save(response)
    return response
