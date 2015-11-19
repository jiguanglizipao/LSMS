import json

from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from aglaia.settings import LOGIN_URL, ACCOUNT_HOME_URL, EMAIL_AUTH_PREFIX
from aglaia.decorators import *
from aglaia.views import show_message, get_context_list, no_excp_post, no_excp_get

from account.views import get_context_user
from computing.models import *
from computing.interface import *
from goods.interface import *
from goods.models import *
from log.models import *
from log.interface import *
from lxml import etree


def get_context_log(lg):
    dc = {}
    dc['actor'] = User.objects.get(id=lg.user_id)
    dc['target'] = lg.get_target_str()
    dc['action'] = lg.action
    dc['time'] = lg.time
    dc['desc'] = lg.description
    return dc


def get_borrow_loglist_context(id, is_actor):
    l = LogBorrow.objects.filter(target__id=id).order_by('time')
    return get_context_list(l, get_context_log)


def get_computing_loglist_context(id, is_actor):
    l = LogComputing.objects.filter(target__id=id).order_by('time')
    return get_context_list(l, get_context_log)


def get_goods_loglist_context(id, is_actor):
    l = LogSingle.objects.filter(target__id=id).order_by('time')
    return get_context_list(l, get_context_log)


def get_account_loglist_context(id, is_actor):
    from itertools import chain
    from django.db.models import Q
    from operator import attrgetter
    l = None
    if is_actor == 'true':
        accountLog = LogAccount.objects.filter(user_id=id)
        brwLog = LogBorrow.objects.filter(user_id=id)
        compLog = LogComputing.objects.filter(user_id=id)
        goodLog = LogSingle.objects.filter(user_id=id)
        l = sorted(
            chain(
                accountLog,
                brwLog,
                compLog,
                goodLog),
            key=attrgetter('time'),
            reverse=False)
    elif is_actor == 'false':
        l = LogAccount.objects.filter(target__user__id=id).order_by('time')
    else:
        accountLog = LogAccount.objects.filter(
            Q(user_id=id) | Q(target__user__id=id))
        brwLog = LogBorrow.objects.filter(user_id=id)
        compLog = LogComputing.objects.filter(user_id=id)
        goodLog = LogSingle.objects.filter(user_id=id)
        l = sorted(
            chain(
                accountLog,
                brwLog,
                compLog,
                goodLog),
            key=attrgetter('time'),
            reverse=False)
    return get_context_list(l, get_context_log)


log_list_func = {
    'goods': get_goods_loglist_context,
    'computing': get_computing_loglist_context,
    'user': get_account_loglist_context,
    'borrow': get_borrow_loglist_context
}


@method_required('GET')
@permission_required(PERM_VIEW_ALL)
def show_log(request):
    # try:
    g = request.GET
    is_actor = None
    if 'is_actor' in g:
        is_actor = g['is_actor']
    llist = log_list_func[g['type']](g['id'], is_actor)
    if len(llist) == 0:
        is_empty = True
    else:
        is_empty = False
    return render(request, 'log.html', {
        'user': get_context_user(request.user),
        'logs': llist,
        'is_empty': is_empty,
        'perm_list': request.user.get_all_permissions()
    })
    # except Exception as e:
    #     return show_message(request, 'Show log Error: ' + e.__str__())


@method_required('GET')
@permission_required(PERM_NORMAL)
def show_message_center(request):
    account = Account.objects.get(user=request.user)
    brws = packed_find_borrow(request, {'account': account}, {})
    comps = packed_find_computing(request, {'account': account}, {})

    goods_time_type = 'Recv_Readed_Time'
    comps_time_type = 'Recv_Readed_Time'
    if request.user.has_perm(GOODS_AUTH):
        brws = packed_find_borrow(request, {}, {})
        goods_time_type = 'Send_Readed_Time'
    if request.user.has_perm(COMPUT_AUTH):
        comps = packed_find_computing(request, {}, {})
        comps_time_type = 'Send_Readed_Time'

    brws = brws.order_by('single', '-id')

    goods = dict()
    brws_dic = dict()
    for brw in brws:
        if brw.single.sn in brws_dic:
            continue
        brws_dic[brw.single.sn] = True
        sn = str(brw.single.sn).replace(" ", "")
        if sn not in goods:
            goods[sn] = {
                'id': sn,
                'name': brw.single.goods.name,
                'user': brw.account,
                'type': brw.single.goods.gtype,
                'msgs': [],
            }
        message = Message(brw.note)
        for i in range(0, message.__sizeof__()):

            msg = {}
            msg['direction'] = message.index(i)["direction"]
            msg['info_type'] = message.index(i)["info_type"]
            msg['associate'] = message.index(i)["user_name"]
            msg['time'] = message.index(i)["time"]
            msg['text'] = message.index(i)["text"]
            msg['flag'] = (message.getTime()[goods_time_type]
                           < msg['time']).__str__()
            if msg['text']:
                goods[sn]['msgs'].append(msg)
        message.setTime(goods_time_type)
        brw.note = message.tostring()
        brw.save()
        goods[sn]['msgs'].sort(key=lambda tmsg: tmsg['time'])
        goods[sn]['msgs'].reverse()

    goodslist = []
    for key in goods:
        goodslist.append(goods[key])
    goodslist.sort(key=lambda tgood: tgood['id'])
    for goodsItem in goodslist:
        if len(goodsItem['msgs']) == 0:
            goodsItem['newMessage'] = False
        else:
            if goodsItem['msgs'][0]['flag'] == 'True':
                goodsItem['newMessage'] = True
            else:
                goodsItem['newMessage'] = False

    compset = dict()
    for comp in comps:
        sn = str(comp.sn).replace(" ", "")
        if sn not in compset:
            compset[sn] = {
                'id': sn,
                'os': comp.os,
                'pc_type': comp.pc_type,
                'flag': str(comp.flag),
                'msgs': [],
            }
        message = Message(comp.note)
        for i in range(0, message.__sizeof__()):
            msg = {}
            msg['direction'] = message.index(i)["direction"]
            msg['info_type'] = message.index(i)["info_type"]
            msg['associate'] = message.index(i)["user_name"]
            msg['time'] = message.index(i)["time"]
            msg['text'] = message.index(i)["text"]
            msg['flag'] = (message.getTime()[comps_time_type]
                           < msg['time']).__str__()
            if msg['text']:
                compset[sn]['msgs'].append(msg)
        message.setTime(comps_time_type)
        comp.note = message.tostring()
        comp.save()
        compset[sn]['msgs'].sort(key=lambda tmsg: tmsg['time'])
        compset[sn]['msgs'].reverse()

    complist = []
    for key in compset:
        complist.append(compset[key])

    complist.sort(key=lambda tcomp: tcomp['id'])

    for compItem in complist:
        if len(compItem['msgs']) == 0:
            compItem['newMessage'] = False
        else:
            if compItem['msgs'][0]['flag'] == 'True':
                compItem['newMessage'] = True
            else:
                compItem['newMessage'] = False
    cont = {
        'curpage': 'message_center',
        'user': get_context_user(request.user),
        'perm_list': request.user.get_all_permissions(),
        'goods': goodslist,
        'complist': complist,
    }
    return render(request, 'message_center.html', cont)
