from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from django.db import models


from aglaia.settings import LOGIN_URL, ACCOUNT_HOME_URL, EMAIL_AUTH_PREFIX, USER_RETURN_MESSAGE, USER_MISS_MESSAGE
from aglaia.views import get_context_list, no_excp_post, no_excp_get
from aglaia.decorators import permission_required, method_required, http_denied, show_denied_message
from aglaia.messages import *
from account.views import get_context_user
from account.models import *
from goods.models import *
from computing.models import *
from account.interface import *
from computing.interface import *
from goods.interface import *
from aglaia.mail_tools import *


from computing.views import get_context_computing, get_context_pack
import json

from aglaia.message_center import Message
from django.core.management import execute_from_command_line
import os
import datetime
import time
from django import forms
import hashlib
import xlrd
import xlsxwriter
from random import Random
import threading

mutex = threading.Lock()


class UploadFileForm(forms.Form):
    file = forms.FileField()


def show_message(request, msg):
    return render(request, "excel_message.html", {'message': msg})


def random_str(randomlength=8):
    ran = str()
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        ran += chars[random.randint(0, length)]
    return ran


def handle_uploaded_file(suffix, f):
    ran = random_str()
    destination = open('excel/' + ran + suffix, 'wb')
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
    ran = 'excel/' + random_str() + '.xml'
    execute_from_command_line(
        ['manage.py', 'dumpdata', '--output', ran, '--format', 'xml', '--indent', '4'])
    file = open(ran)
    data = file.read()
    file.close()
    data = make_hash(data) + '\n' + data
    filename = time.strftime(
        '%Y-%m-%d_%H:%M:%S',
        time.localtime(
            time.time())) + '.xml'
    response = StreamingHttpResponse(data)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename=' + filename
    os.remove(ran)
    return response


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def import_database(request):
    try:
        ran = 'excel/' + request.GET['ran'] + '.xml'
        file = open(ran)
        hash = file.readline().replace('\n', '')
        data = file.read()
        file.close()
        os.remove(ran)
        if hash != make_hash(data):
            return show_message(request, 'Import Error File Destroyed')
        file = open(ran, 'w')
        file.write(data)
        file.close()

        Single.objects.all().delete()
        Goods.objects.all().delete()
        GType.objects.all().delete()
        Apply_Goods.objects.all().delete()

        Computing.objects.all().delete()
        Server.objects.all().delete()
        Package.objects.all().delete()

        LogAccount.objects.all().delete()
        LogComputing.objects.all().delete()
        LogBorrow.objects.all().delete()
        LogSingle.objects.all().delete()

        execute_from_command_line(['manage.py', 'loaddata', ran])
        os.remove(ran)
        return show_message(request, 'Import Success')

    except Exception as e:
        return show_message(request, 'Import Error' + e.__str__())


@permission_required(PERM_GOODS_AUTH)
def index(request):
    if request.method == 'GET':
        return render(request, "excel_index.html", {
            'user': get_context_user(request.user),
            'perm_list': request.user.get_all_permissions()})

    if 'xml' in request.FILES:
        ran = handle_uploaded_file('.xml', request.FILES['xml'])
        return HttpResponseRedirect('import_database?ran=' + ran)
    elif 'xlsx' in request.FILES:
        ran = handle_uploaded_file('.xlsx', request.FILES['xlsx'])
        return HttpResponseRedirect('import_excel?ran=' + ran)
    else:
        return show_message(request, 'Upload Error')


def export_excel(request):
    ran = 'excel/' + random_str() + '.xlsx'
    workbook = xlsxwriter.Workbook(ran)

    sheet = workbook.add_worksheet('在库物品')
    sheet.write(0, 0, '物品名')
    sheet.write(0, 1, 'SN号')
    sheet.write(0, 2, '物品种类')
    sheet.merge_range(0, 3, 0, 128, '物品属性')
    singles = Single.objects.all().filter(status=AVALIABLE_KEY)
    i = 1
    for item in singles:
        sheet.write(i, 0, item.goods.name)
        sheet.write(i, 1, item.sn)
        sheet.write(i, 2, item.goods.gtype.name)
        pro_names = item.goods.gtype.pro_names
        pro_names = pro_names.split(',')
        pro_values = item.goods.pro_values
        pro_values = pro_values.split(sep)
        j = 0
        for pro in pro_names:
            if not pro:
                continue
            sheet.write(i, 3 + j, pro + " : " + pro_values[j])
            j += 1
        i += 1

    sheet = workbook.add_worksheet('借出物品')
    sheet.write(0, 0, '物品名')
    sheet.write(0, 1, 'SN号')
    sheet.write(0, 2, '借用者')
    sheet.write(0, 3, '借用状态')
    sheet.write(0, 4, '物品种类')
    sheet.merge_range(0, 5, 0, 128, '物品属性')
    singles = Single.objects.all()
    singles = singles.exclude(status=AVALIABLE_KEY)
    singles = singles.exclude(status=DESTROYED_KEY)
    singles = singles.exclude(status=LOST_KEY)

    i = 1
    for item in singles:
        sheet.write(i, 0, item.goods.name)
        sheet.write(i, 1, item.sn)
        sheet.write(i, 2, item.user_name)
        sheet.write(i, 3, item.get_status_display())
        sheet.write(i, 4, item.goods.gtype.name)
        pro_names = item.goods.gtype.pro_names
        pro_names = pro_names.split(',')
        pro_values = item.goods.pro_values
        pro_values = pro_values.split(sep)
        j = 0
        for pro in pro_names:
            if not pro:
                continue
            sheet.write(i, 5 + j, pro + " : " + pro_values[j])
            j += 1
        i += 1

    sheet = workbook.add_worksheet('申请物资')
    sheet.write(0, 0, '物品名')
    sheet.write(0, 1, 'SN号')
    sheet.write(0, 2, '申请者')
    sheet.write(0, 3, '申请状态')
    sheet.write(0, 4, '物品种类')
    sheet.merge_range(0, 5, 0, 128, '物品属性')
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
            sheet.write(i, 5 + j, pro + " : " + pro_values[j])
            j += 1
        i += 1

    sheet = workbook.add_worksheet('计算资源')
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
    singles = singles.exclude(status='')

    i = 1
    for item in singles:
        sheet.write(i, 0, item.name)
        sheet.write(i, 1, item.sn)
        sheet.write(i, 2, item.account.user.username)
        sheet.write(i, 3, item.get_status_display())
        dic = {PHYSICAL_MACHINE_KEY: '实体机', VIRTUAL_MACHINE_KEY: '虚拟机'}
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

    workbook.close()
    response = HttpResponse(
        open(
            ran,
            'rb').read(),
        content_type='application/vnd.ms-excel')
    filename = time.strftime(
        '%Y-%m-%d_%H:%M:%S',
        time.localtime(
            time.time())) + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename
    os.remove(ran)
    return response


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def import_excel(request):
    ran = 'excel/' + request.GET['ran'] + '.xlsx'

    try:
        workbook = xlrd.open_workbook(ran)
        os.remove(ran)

        # 在库物品
        assert workbook.sheet_by_index(0).name == '在库物品'
        single_change = list()
        sheet = workbook.sheet_by_index(0)
        assert sheet.cell(0, 0).value == '物品名'
        assert sheet.cell(0, 1).value == 'SN号'
        assert sheet.cell(0, 2).value == '物品种类'
        assert sheet.cell(0, 3).value == '物品属性'
        nrows = sheet.nrows
        ncols = sheet.ncols
        singles = Single.objects.all()
        for i in range(1, nrows):
            assert len(
                GType.objects.all().filter(
                    name=sheet.cell(
                        i, 2).value)) >= 1
            gtype = GType.objects.all().filter(name=sheet.cell(i, 2).value)[0]
            pro_names = gtype.pro_names.split(',')
            pro_values = str()
            dic = dict()
            for j in range(3, len(sheet.row(i))):
                if sheet.cell(i, j).value.find(':') != -1:
                    temp = sheet.cell(i, j).value.split(':')
                    dic[temp[0].strip()] = temp[1].strip()
                else:
                    continue

            prop = list()
            for pro in pro_names:
                if not pro:
                    continue
                assert pro in dic
                pro_values += dic[pro] + sep
                prop.append({'pro_name': pro, 'pro_value': dic[pro]})

            if len(singles.filter(sn=sheet.cell(i, 1).value)) == 0:
                single_change.append({'type': 'create',
                                      'name': sheet.cell(i, 0).value,
                                      'sn': sheet.cell(i, 1).value,
                                      'type_name': gtype.name,
                                      'values': pro_values,
                                      'prop': prop,
                                      'id': str(len(single_change)),
                                      })
            else:
                item = singles.filter(sn=sheet.cell(i, 1).value)[0]
                assert item.status == AVALIABLE_KEY
                if item.goods.name == sheet.cell(
                        i, 0).value and item.goods.gtype.name == gtype.name and item.goods.pro_values == pro_values:
                    continue
                single_change.append({'type': 'change',
                                      'name': sheet.cell(i, 0).value,
                                      'sn': sheet.cell(i, 1).value,
                                      'type_name': gtype.name,
                                      'values': pro_values,
                                      'prop': prop,
                                      'id': str(len(single_change)),
                                      })

        # 计算资源
        assert workbook.sheet_by_index(3).name == '计算资源'
        computing_change = list()
        sheet = workbook.sheet_by_index(3)
        assert sheet.cell(0, 0).value == '资源名'
        assert sheet.cell(0, 1).value == 'SN号'
        assert sheet.cell(0, 2).value == '借用者'
        assert sheet.cell(0, 3).value == '借用状态'
        assert sheet.cell(0, 4).value == '套餐名'
        assert sheet.cell(0, 5).value == '资源种类'
        assert sheet.cell(0, 6).value == 'CPU种类'
        assert sheet.cell(0, 7).value == '内存大小'
        assert sheet.cell(0, 8).value == '硬盘种类'
        assert sheet.cell(0, 9).value == '硬盘大小'
        assert sheet.cell(0, 10).value == '操作系统'
        assert sheet.cell(0, 11).value == '期满时间'
        assert sheet.cell(0, 12).value == '用户名'
        assert sheet.cell(0, 13).value == '密码'
        assert sheet.cell(0, 14).value == 'IP'
        assert sheet.cell(0, 15).value == '是否有重要数据'
        assert sheet.cell(0, 16).value == '重要数据内容'

        nrows = sheet.nrows
        ncols = sheet.ncols
        computings = Computing.objects.all()
        for i in range(1, nrows):
            assert len(
                Account.objects.all().filter(
                    user__username=sheet.cell(
                        i, 2).value)) >= 1
            STATUS_CHOICES = {
                VERIFYING: VERIFYING_KEY,
                VERIFY_FAIL: VERIFY_FAIL_KEY,
                VERIFY_SUCCESS: VERIFY_SUCCESS_KEY,
                BORROWED: BORROWED_KEY,
                MODIFY_APPLY: MODIFY_APPLY_KEY,
                RETURNING: RETURNING_KEY,
                RETURNED: RETURNED_KEY,
            }
            TYPE_CHOICES = {
                '实体机': PHYSICAL_MACHINE_KEY,
                '虚拟机': VIRTUAL_MACHINE_KEY}
            DISK_CHOICES = {MACHINE: MACHINE_KEY, SSD: SSD_KEY}
            assert sheet.cell(i, 3).value in STATUS_CHOICES
            assert sheet.cell(i, 5).value in TYPE_CHOICES
            assert sheet.cell(i, 8).value in DISK_CHOICES
            date = time.strptime(sheet.cell(i, 11).value, '%Y-%m-%d')
            assert sheet.cell(i, 15).value in ['True', 'False', ]

            if len(computings.filter(sn=sheet.cell(i, 1).value)) == 0:
                computing_change.append({'type': 'create',
                                         'name': sheet.cell(i, 0).value,
                                         'sn': sheet.cell(i, 1).value,
                                         'user': sheet.cell(i, 2).value,
                                         'status': sheet.cell(i, 3).value,
                                         'pack_name': sheet.cell(i, 4).value,
                                         'pc_type': sheet.cell(i, 5).value,
                                         'cpu': sheet.cell(i, 6).value,
                                         'memory': sheet.cell(i, 7).value,
                                         'disk_type': sheet.cell(i, 8).value,
                                         'disk': sheet.cell(i, 9).value,
                                         'os': sheet.cell(i, 10).value,
                                         'expire_time': sheet.cell(i, 11).value,
                                         'login': sheet.cell(i, 12).value,
                                         'password': sheet.cell(i, 13).value,
                                         'ip': sheet.cell(i, 14).value,
                                         'flag': sheet.cell(i, 15).value,
                                         'data_content': sheet.cell(i, 16).value,
                                         'id': str(len(computing_change))
                                         })
            else:
                dic = {PHYSICAL_MACHINE_KEY: '实体机', VIRTUAL_MACHINE_KEY: '虚拟机'}
                item = computings.filter(sn=sheet.cell(i, 1).value)[0]
                if (item.name == sheet.cell(i, 0).value and
                        item.sn == sheet.cell(i, 1).value and
                        item.account.user.username == sheet.cell(i, 2).value and
                        item.get_status_display() == sheet.cell(i, 3).value and
                        item.pack_name == sheet.cell(i, 4).value and
                        dic[item.pc_type] == sheet.cell(i, 5).value and
                        item.cpu == sheet.cell(i, 6).value and
                        item.memory == sheet.cell(i, 7).value and
                        item.get_disk_type_display() == sheet.cell(i, 8).value and
                        item.disk == sheet.cell(i, 9).value and
                        item.os == sheet.cell(i, 10).value and
                        str(item.expire_time) == sheet.cell(i, 11).value and
                        item.login == sheet.cell(i, 12).value and
                        item.password == sheet.cell(i, 13).value and
                        item.address == sheet.cell(i, 14).value and
                        item.flag == bool(sheet.cell(i, 15).value) and
                        item.data_content == sheet.cell(i, 16).value):
                    continue
                computing_change.append({'type': 'change',
                                         'name': sheet.cell(i, 0).value,
                                         'sn': sheet.cell(i, 1).value,
                                         'user': sheet.cell(i, 2).value,
                                         'status': sheet.cell(i, 3).value,
                                         'pack_name': sheet.cell(i, 4).value,
                                         'pc_type': sheet.cell(i, 5).value,
                                         'cpu': sheet.cell(i, 6).value,
                                         'memory': sheet.cell(i, 7).value,
                                         'disk_type': sheet.cell(i, 8).value,
                                         'disk': sheet.cell(i, 9).value,
                                         'os': sheet.cell(i, 10).value,
                                         'expire_time': sheet.cell(i, 11).value,
                                         'login': sheet.cell(i, 12).value,
                                         'password': sheet.cell(i, 13).value,
                                         'ip': sheet.cell(i, 14).value,
                                         'flag': sheet.cell(i, 15).value,
                                         'data_content': sheet.cell(i, 16).value,
                                         'id': str(len(computing_change))
                                         })

        return render(
            request, 'excel_list.html', {
                'goods_list': single_change, 'computing_list': computing_change})

    except Exception as e:
        return show_message(request, 'Import Error ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def import_goods(request):
    try:
        mutex.acquire()
        if request.POST['type'] == 'create':
            gtype = GType.objects.all().filter(
                name=request.POST['type_name'])[0]
            goods = Goods(
                name=request.POST['name'],
                gtype=gtype,
                pro_values=request.POST['pro_values'])
            goods.save()
            single = Single(
                sn=request.POST['sn'],
                goods=goods,
                status=AVALIABLE_KEY,
                note='管理员创建',
                user_name='')
            single.save()

        if request.POST['type'] == 'change':
            single = Single.objects.all().filter(sn=request.POST['sn'])[0]
            gtype = GType.objects.all().filter(
                name=request.POST['type_name'])[0]
            goods = Goods(
                name=request.POST['name'],
                gtype=gtype,
                pro_values=request.POST['pro_values'])
            goods.save()
            single.goods = goods
            single.save()

        mutex.release()
        return HttpResponse('Success')
    except Exception as e:
        mutex.release()
        return HttpResponse('Error ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def import_computing(request):
    try:
        mutex.acquire()
        if request.POST['type'] == 'create':
            expire_time = datetime.datetime.strptime(
                request.POST['expire_time'], '%Y-%m-%d')
            account = Account.objects.all().filter(
                user__username=request.POST['user'])[0]
            STATUS_CHOICES = {
                VERIFYING: VERIFYING_KEY,
                VERIFY_FAIL: VERIFY_FAIL_KEY,
                VERIFY_SUCCESS: VERIFY_SUCCESS_KEY,
                BORROWED: BORROWED_KEY,
                MODIFY_APPLY: MODIFY_APPLY_KEY,
                RETURNING: RETURNING_KEY,
                RETURNED: RETURNED_KEY,
            }
            TYPE_CHOICES = {
                '实体机': PHYSICAL_MACHINE_KEY,
                '虚拟机': VIRTUAL_MACHINE_KEY}
            DISK_CHOICES = {MACHINE: MACHINE_KEY, SSD: SSD_KEY}
            status = STATUS_CHOICES[request.POST['status']]
            pc_type = TYPE_CHOICES[request.POST['pc_type']]
            disk_type = DISK_CHOICES[request.POST['disk_type']]
            message = Message()
            message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.POST['user'], 'text': '管理员创建'})
            computing = Computing(
                pc_type=pc_type,
                cpu=request.POST['cpu'],
                memory=int(
                    float(
                        request.POST['memory'])),
                disk=int(
                    float(
                        request.POST['disk'])),
                disk_type=disk_type,
                os=request.POST['os'],
                sn=request.POST['sn'],
                expire_time=expire_time,
                login=request.POST['login'],
                password=request.POST['password'],
                status=status,
                account=account,
                note=message.tostring(),
                address=request.POST['ip'],
                flag=request.POST['flag'],
                name=request.POST['name'],
                pack_name=request.POST['pack_name'],
                data_content=request.POST['data_content'])
            computing.save()

        if request.POST['type'] == 'change':
            computing = Computing.objects.all().filter(
                sn=request.POST['sn'])[0]
            note = computing.note
            computing.delete()
            expire_time = datetime.datetime.strptime(
                request.POST['expire_time'], '%Y-%m-%d')
            account = Account.objects.all().filter(
                user__username=request.POST['user'])[0]
            STATUS_CHOICES = {
                VERIFYING: VERIFYING_KEY,
                VERIFY_FAIL: VERIFY_FAIL_KEY,
                VERIFY_SUCCESS: VERIFY_SUCCESS_KEY,
                BORROWED: BORROWED_KEY,
                MODIFY_APPLY: MODIFY_APPLY_KEY,
                RETURNING: RETURNING_KEY,
                RETURNED: RETURNED_KEY,
            }
            TYPE_CHOICES = {
                '实体机': PHYSICAL_MACHINE_KEY,
                '虚拟机': VIRTUAL_MACHINE_KEY}
            DISK_CHOICES = {MACHINE: MACHINE_KEY, SSD: SSD_KEY}
            status = STATUS_CHOICES[request.POST['status']]
            pc_type = TYPE_CHOICES[request.POST['pc_type']]
            disk_type = DISK_CHOICES[request.POST['disk_type']]
            computing = Computing(
                pc_type=pc_type,
                cpu=request.POST['cpu'],
                memory=int(
                    float(
                        request.POST['memory'])),
                disk=int(
                    float(
                        request.POST['disk'])),
                disk_type=disk_type,
                os=request.POST['os'],
                sn=request.POST['sn'],
                expire_time=expire_time,
                login=request.POST['login'],
                password=request.POST['password'],
                status=status,
                account=account,
                note=note,
                address=request.POST['ip'],
                flag=request.POST['flag'],
                name=request.POST['name'],
                pack_name=request.POST['pack_name'],
                data_content=request.POST['data_content'])
            computing.save()

        mutex.release()
        return HttpResponse('Success')

    except Exception as e:
        mutex.release()
        return HttpResponse('Error ' + e.__str__())
