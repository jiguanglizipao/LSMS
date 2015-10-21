from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required

import computing
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

sgl_sta_map = {
    'available': AVALIABLE_KEY,
    'unavailable': UNAVALIABLE_KEY,
    'destroyed': DESTROYED_KEY,
    'borrowed': BORROWED_KEY,
    'lost': LOST_KEY,
    'repairing': REPAIRING_KEY,
}


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================


def get_pack_name(pack):
    return pack.name


def get_context_single(sgl):
    good = sgl.goods
    tp = good.gtype
    dc = {}
    dc['id'] = sgl.id
    dc['name'] = good.name
    dc['type_id'] = tp.id
    dc['type_name'] = tp.name
    dc['sn'] = sgl.sn
    dc['status'] = sgl.get_status_display()
    try:
        dc['user_name'] = Account.objects.get(
            user__username=sgl.user_name).real_name
        dc['user_id'] = sgl.user_name
    except:
        dc['user_id'] = ''
        dc['user_name'] = ''
    dc['note'] = sgl.note
    props = []
    for i in range(0, tp.get_pronum()):
        props.append({'pro_name': tp.get_proname(i),
                      'pro_value': good.get_pro(i)})
    dc['prop'] = props
    return dc


def get_context_borrow(brw):
    dc = {}
    dc['id'] = brw.id
    dc['sn'] = brw.single.sn
    dc['goods_name'] = brw.single.goods.name
    dc['borrower_name'] = brw.account.user.username
    dc['note'] = Message(brw.note).last()['text']
    return dc


def get_context_apply_goods(brw):
    dc = {}
    dc['id'] = brw.id
    dc['sn'] = brw.sn
    dc['name'] = brw.name
    dc['applyer_name'] = brw.account.user.username
    dc['note'] = brw.note  # Message(brw.note).last()['text']
    # OnionYST
    dc['type_name'] = brw.type_name
    pro_names = brw.pro_names.split(sep)
    pro_values = brw.pro_values.split(sep)
    props = []
    for i in range(0, len(pro_names)):
        if pro_names[i]:
            props.append({
                'pro_name': pro_names[i],
                'pro_value': pro_values[i],
            })
    dc['prop'] = props
    return dc


def get_context_userbrw(brw):
    dc = {}
    dc['id'] = brw.id
    dc['sn'] = brw.single.sn
    dc['name'] = brw.single.goods.name
    dc['note'] = Message(brw.note).last()['text']
    return dc


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def add_goods(request):
    ''' Add new goods with new pro values '''
    try:
        name = request.POST['name']
        type_name = request.POST['type_name']

        tp = packed_find_gtypes(request, type_name)
        if not tp or len(tp) > 1:
            raise Exception('No Such Goods Type')
        tp = tp[0]

        type_value = []
        for i in range(1, tp.get_pronum() + 1):
            prop_key = "pro" + str(i) + "_value"
            type_value.append(request.POST[prop_key])

        gd = packed_create_goods(request, name, tp, type_value)
        sns = request.POST['sn'].split(',')
        packed_create_single(request, gd, sns, AVALIABLE_KEY, '')

        return HttpResponseRedirect(reverse("goods.views.show_list"))
    except KeyError as e:
        return show_message(request, 'Key not found: ' + e.__str__())
    except Exception as e:
        return show_message(request, "Add goods failed: " + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def apply_goods(request):
    ''' Apply new goods with new pro values '''
    try:
        name = request.POST['name']
        type_name = request.POST['type_name']
        ext_num = request.POST['ext_num']
        note = request.POST['note']

        pro_name = []
        pro_value = []

        tp = packed_find_gtypes(request, type_name)
        tp_len = 0
        if tp and len(tp) == 1:
            tp = tp[0]
            tp_len = tp.get_pronum()
            for i in range(1, tp_len + 1):
                prop_key = "pro" + str(i) + "_value"
                pro_value.append(request.POST[prop_key])
                pro_name.append(tp.get_proname(i - 1))

        for i in range(1, int(ext_num) + 1):
            prop_key = "pro" + str(tp_len + i)
            pro_name.append(request.POST[prop_key + "_name"])
            pro_value.append(request.POST[prop_key + "_value"])

        sns = request.POST['sn'].split(',')
        account = Account.objects.get(user=request.user)

        packed_create_apply_goods(
            request, name, type_name, pro_name, pro_value,
            sns, GOODS_APPLY_KEY, account, note
        )

        return HttpResponseRedirect(reverse("goods.views.show_list"))
    except KeyError as e:
        return show_message(request, 'Key not found: ' + e.__str__())
    except Exception as e:
        return show_message(request, "Apply goods failed: " + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH, http_denied)
def do_type_props(request):
    '''list all the properties' name of a type'''
    try:
        type_name = request.POST['type_name']
        gtype = packed_find_gtypes(request, type_name)
        pros = []
        if gtype:
            pros = gtype[0].get_all_pros()
        return HttpResponse(json.dumps({
            "pro_names": pros
        }))
    except Exception as e:
        # print(e)
        return show_message(request, "Find goods type failed: " + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def add_type(request):
    '''list all the properties' name of a type'''
    try:
        type_name = request.POST['type_name']

        gtype = packed_find_gtypes(request, type_name)
        if gtype:
            raise Exception('type name exist!')

        type_key = []
        for i in range(1, 33):
            prop_key = "pro" + str(i) + "_name"
            pv = no_excp_post(request, prop_key)
            if pv:
                type_key.append(pv)
        if not type_key:
            raise Exception('No Type contrib Added!')
        # Add new type to the database
        packed_create_gtype(request, type_name, type_key)
        # On success
        return HttpResponseRedirect(reverse('goods.views.show_add_goods'))
    except Exception as e:
        return show_message(
            request,
            'Some thing Wrong While adding type: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_accept_borrow(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROW_AUTHING_KEY:
            return show_message(
                request, 'This Request is not under verifying!')
        if not brw.single.status == AVALIABLE_KEY:
            return show_message(request, 'The good is not avaliable!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(
            request, id, {
                'status': ACCEPTED_KEY, 'note': message.tostring()}, log=get_accept_brw_log())
        send_notify_mail(request, AcceptBrwMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Accept borrow failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_reject_borrow(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROW_AUTHING_KEY:
            return show_message(
                request, 'This Request is not under verifying!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': REJECTED_KEY,
                              'note': message.tostring()},
                             log=get_reject_brw_log(brw))
        send_notify_mail(request, RejectBrwMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Reject borrow failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_finish_borrow(request):
    try:
        id = request.POST['id']

        brw = Borrow.objects.get(id=id)

        if not brw.status == ACCEPTED_KEY:
            return show_message(request, 'This Request is not accepted!')
        if not brw.single.status == AVALIABLE_KEY:
            packed_update_borrow(
                request, id, {
                    'status': BORROW_AUTHING_KEY}, log=get_wrong_goods_status_log())
            return show_message(request, 'The good is not avaliable!')

        packed_update_single(request,
                             brw.single.id,
                             {'status': BORROWED_KEY,
                              'user_name': brw.account.user.username},
                             log=get_good_brwed_log())
        packed_update_borrow(
            request, id, {
                'status': BORROWED_KEY}, log=get_finish_brw_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Finish borrow failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_accept_return(request):
    try:
        id = request.POST['id']

        brw = Borrow.objects.get(id=id)
        note = request.POST['note']
        lost = request.POST['lost']

        if not brw.status == RETURN_AUTHING_KEY:
            return show_message(
                request, 'This Request is not in a return auth status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        if (lost == 'false'):
            packed_update_borrow(request,
                                 id,
                                 {'status': RETURN_PENDING_KEY,
                                  'note': message.tostring()},
                                 log=get_accept_ret_log())
        else:
            packed_update_borrow(
                request, id, {
                    'status': LOST_KEY, 'note': message.tostring()}, log=get_lost_ret_log())
            packed_update_single(
                request, brw.single.id, {
                    'status': LOST_KEY}, log=get_good_lost_log())
        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Accept return failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_finish_return(request):
    try:
        id = request.POST['id']
        intect = request.POST['intact']

        brw = Borrow.objects.get(id=id)

        if not brw.status == RETURN_PENDING_KEY:
            return show_message(
                request, 'This Request is not accepted to return!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')
        if intect == 'true':
            packed_update_single(
                request, brw.single.id, {
                    'status': AVALIABLE_KEY, 'user_name': ''}, log=get_good_reted_log())
            packed_update_borrow(
                request, id, {
                    'status': RETURNED_KEY}, log=get_brw_reted_log())
        else:
            packed_update_single(
                request, brw.single.id, {
                    'status': UNAVALIABLE_KEY}, log=get_good_dmg_log())
            packed_update_borrow(
                request, id, {
                    'status': DAMAGED_KEY}, log=get_brw_dmg_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Finish return failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_accept_repair(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == REPAIR_APPLY_KEY:
            return show_message(
                request, 'This Request is not in a repair apply status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': REPAIR_PEND_KEY,
                              'note': message.tostring()},
                             log=get_accept_repair_log())
        # send_notify_mail(request, AcceptRepairMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Accept Repair failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_accept_destroy(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == DESTROY_APPLY_KEY:
            return show_message(
                request, 'This Request is not in a destroy apply status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': DESTROY_ACCEPT_KEY,
                              'note': message.tostring()},
                             log=get_accept_destroy_log())

        packed_update_single(
            request, brw.single.id, {
                'status': DESTROYED_KEY}, log=get_good_destroy_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Accept Destroy failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_reject_repair(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == REPAIR_APPLY_KEY:
            return show_message(
                request, 'This Request is not in a repair apply status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': BORROWED_KEY,
                              'note': message.tostring()},
                             log=get_reject_repair_log())
        send_notify_mail(request, RejectRepairMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Reject Repair failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_reject_destroy(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == DESTROY_APPLY_KEY:
            return show_message(
                request, 'This Request is not in a destroy apply status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': BORROWED_KEY,
                              'note': message.tostring()},
                             log=get_reject_repair_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Reject Destroy failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_start_repair(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == REPAIR_PEND_KEY:
            return show_message(
                request, 'This Request is not in a repair pend status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': REPAIRING_KEY,
                              'note': message.tostring()},
                             log=get_brw_repairing_log())
        packed_update_single(
            request, brw.single.id, {
                'status': REPAIRING_KEY}, log=get_good_repairing_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Start Repair failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_finish_repair(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == REPAIRING_KEY:
            return show_message(
                request, 'This Request is not in a repairing status!')
        if not brw.single.status == REPAIRING_KEY:
            return show_message(
                request, 'The good is not in a repairing status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': FINISH_REPAIR_KEY,
                              'note': message.tostring()},
                             log=get_finish_repair_log())
        send_notify_mail(request, FinishRepairMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Finish Repair failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_return_repair(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == FINISH_REPAIR_KEY:
            return show_message(
                request, 'This Request is not in a finish repair status!')
        if not brw.single.status == REPAIRING_KEY:
            return show_message(
                request, 'The good is not in a repairing status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': BORROWED_KEY,
                              'note': message.tostring()},
                             log=get_ret_repaired_log())
        packed_update_single(
            request, brw.single.id, {
                'status': BORROWED_KEY}, log=get_good_repaired_log())

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Return Repair failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_accept_apply_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        apgd = Apply_Goods.objects.get(id=id)

        if not apgd.status == GOODS_APPLY_KEY:
            return show_message(request, 'This Request is not in a apply_goods apply satus!')

        packed_update_apply_goods(request, id,
                                  {'status': GOODS_APPLY_PEND_KEY, 'note': note},
                                  log=get_accept_apply_goods_log())
        # sent_notify_mail

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Accept Apply_Goods failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_reject_apply_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        apgd = Apply_Goods.objects.get(id=id)

        if not apgd.status == GOODS_APPLY_KEY:
            return show_message(
                request, "This Request is not in a apply_goods apply status!")

        packed_update_apply_goods(request, id,
                                  {'status': GOODS_APPLY_REJECT_KEY, 'note': note},
                                  log=get_reject_apply_goods_log())

        # send_notify_mail

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Reject Apply_Goods failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_start_apply_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        apgd = Apply_Goods.objects.get(id=id)

        if not apgd.status == GOODS_APPLY_PEND_KEY:
            return show_message(
                request, "This Request is not in a apply_goods apply status!")

        packed_update_apply_goods(request, id,
                                  {'status': GOODS_APPLYING_KEY, 'note': note},
                                  log=get_apply_goods_applying_log())
        # send_notify_mail

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Reject Apply_Goods failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_finish_apply_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        apgd = Apply_Goods.objects.get(id=id)

        if not apgd.status == GOODS_APPLYING_KEY:
            return show_message(
                request, "This Request is not in a apply_goods apply status!")

        packed_update_apply_goods(request, id,
                                  {'status': FINISH_GOODS_APPLY_KEY, 'note': note},
                                  log=get_finish_goods_apply_log())

        # send_notify_mail

        return HttpResponseRedirect(reverse('goods.views.show_manage'))

    except Exception as e:
        return show_message(request, 'Reject Apply_Goods failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_input_apply_goods(request):
    try:
        id = request.POST['id']
        sn = request.POST['sn']
        name = request.POST['name']
        type_name = request.POST['type_name']
        note = request.POST['note']

        apgd = Apply_Goods.objects.get(id=id)

        if packed_find_single(request, {'sn': sn}, {}):
            raise Exception("sn already exists")
        tp = packed_find_gtypes(request, type_name)
        if tp and tp[0].get_all_pros() != apgd.pro_names.split(sep):
            raise Exception("type cannot use this name")
        if not apgd.status == FINISH_GOODS_APPLY_KEY:
            return show_message(request, "This Request is not in a apply_goods finish status!")

        packed_update_apply_goods(
            request, id, {
                'status': INPUT_GOODS_APPLY_KEY, 'note': note, 'sn': sn, 'name': name, 'type_name': type_name
            }, log=get_input_goods_apply_log()
        )

        type_key = []
        for name in apgd.pro_names.split(sep):
            if name:
                type_key.append(name)
        tp = packed_create_gtype(request, type_name, type_key)
        type_value = []
        for value in apgd.pro_values.split(sep):
            if value:
                type_value.append(value)
        gd = packed_create_goods(request, name, tp, type_value)
        sns = sn.split(',')
        packed_create_single(request, gd, sns, AVALIABLE_KEY, '')

        # send_notify_mail
        return HttpResponseRedirect(reverse('goods.views.show_manage'))
    except Exception as e:
        return show_message(request, 'Input Apply_Goods failed: ' + e.__str__())


# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
# -------------------------
@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_set_unavailable(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        sgl = Single.objects.get(id=id)
        if not sgl.status == AVALIABLE_KEY:
            return show_message(
                request, 'The goods cannot be set to unavailable!')
        packed_update_single(
            request, id, {
                'status': UNAVALIABLE_KEY, 'note': note}, log=get_good_unvail_log())
        return HttpResponseRedirect(reverse("goods.views.show_list"))
    except Exception as e:
        return show_message(
            request,
            'Set single good unavailable failed: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_set_available(request):
    try:
        id = request.POST['id']

        sgl = Single.objects.get(id=id)
        if not sgl.status == UNAVALIABLE_KEY:
            return show_message(
                request, 'The goods cannot be set to available!')

        packed_update_single(
            request, id, {
                'status': AVALIABLE_KEY}, log=get_good_avail_log())

        return HttpResponseRedirect(reverse("goods.views.show_list"))
    except Exception as e:
        return show_message(
            request,
            'Set single good available failed: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def do_destroy(request):
    try:
        id = request.POST['id']

        packed_update_single(
            request, id, {
                'status': DESTROYED_KEY}, log=get_good_destroy_log())

        return HttpResponseRedirect(reverse("goods.views.show_list"))
    except Exception as e:
        return show_message(
            request,
            'Set single good destroyed failed: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_borrow(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        sgl = Single.objects.get(id=id)
        if not sgl.status == AVALIABLE_KEY:
            return show_message(request, 'The good is not avaliable!')
        account = Account.objects.get(user=request.user)

        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': request.user.username, 'text': note})
        brw = packed_create_borrow(
            request,
            sn=sgl.sn,
            status=BORROW_AUTHING_KEY,
            note=message.tostring(),
            account=account,
            log=get_brw_requst_log())

        send_notify_mail(request, BrwRequstMail, borrow=brw)

        return HttpResponseRedirect(reverse("goods.views.show_borrow"))
    except Exception as e:
        return show_message(request, 'Borrow request failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_return_goods(request):
    try:
        id = request.POST['id']
        note = USER_RETURN_MESSAGE

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROWED_KEY:
            return show_message(
                request, 'This Request is not in a borrowed status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': RETURN_AUTHING_KEY,
                              'note': message.tostring()},
                             log=get_ret_request_log())
        send_notify_mail(request, RetRequstMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_borrow'))
    except Exception as e:
        return show_message(request, 'Return request failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_miss_goods(request):
    try:
        id = request.POST['id']
        note = USER_MISS_MESSAGE

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROWED_KEY:
            return show_message(
                request, 'This Request is not in a borrowed status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': RETURN_AUTHING_KEY,
                              'note': message.tostring()},
                             log=get_miss_request_log())
        send_notify_mail(request, MissRequstMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_borrow'))
    except Exception as e:
        return show_message(request, 'Miss request failed: ' + e.__str__())


##############################
@method_required('POST')
@permission_required(PERM_NORMAL)
def do_destroy_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROWED_KEY:
            return show_message(
                request, 'This Request is not in a borrowed status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': DESTROY_APPLY_KEY,
                              'note': message.tostring()},
                             log=get_destroy_apply_log())
        # send_notify_mail(request, RepairRequstMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_borrow'))

    except Exception as e:
        return show_message(request, 'Destroy apply failed: ' + e.__str__())


##############################


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_repair_goods(request):
    try:
        id = request.POST['id']
        note = request.POST['note']

        brw = Borrow.objects.get(id=id)

        if not brw.status == BORROWED_KEY:
            return show_message(
                request, 'This Request is not in a borrowed status!')
        if not brw.single.status == BORROWED_KEY:
            return show_message(
                request, 'The good is not in a borrowed status!')

        message = Message(brw.note)
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': request.user.username, 'text': note})

        packed_update_borrow(request,
                             id,
                             {'status': REPAIR_APPLY_KEY,
                              'note': message.tostring()},
                             log=get_repair_apply_log())
        send_notify_mail(request, RepairRequstMail, borrow=brw)

        return HttpResponseRedirect(reverse('goods.views.show_borrow'))

    except Exception as e:
        return show_message(request, 'Repair apply failed: ' + e.__str__())


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def show_add_goods(request):
    type_list = []
    for t in GType.objects.all():
        type_list.append(t.name)
    return render(request, "add_goods.html", {
        'user': get_context_user(request.user),
        "type_list": type_list,
    })


@method_required('GET')
@permission_required(PERM_NORMAL)
def show_apply_goods(request):
    type_list = []
    for t in GType.objects.all():
        type_list.append(t.name)
    return render(request, "apply_goods.html", {
        'user': get_context_user(request.user),
        "type_list": type_list,
    })


@method_required('GET')
@permission_required(PERM_NORMAL)
def show_list(request):
    status = no_excp_get(request, "status")
    name = no_excp_get(request, "name")
    type_name = no_excp_get(request, "type")

    tp_list = []
    for tp in GType.objects.all():
        tp_list.append(tp.name)

    singles = None
    if not status or status == 'all':
        singles = Single.objects.exclude(status=DESTROYED_KEY)
    else:
        singles = Single.objects.filter(status=sgl_sta_map[status])

    if type_name:
        singles = singles.filter(goods__gtype__name__startswith=type_name)
    if name:
        singles = singles.filter(goods__name__startswith=name)

    sgl_list = get_context_list(singles, get_context_single)

    perm_list = request.user.get_all_permissions()

    return render(request, "goods_list.html", {
        'user': get_context_user(request.user),
        "goods_list": sgl_list,
        "type_list": tp_list,
        "perm_list": perm_list
    })


@login_required
def show_borrow(request):
    cont = {}
    cont['curpage'] = 'borrow'

    account = Account.objects.get(user=request.user)

    inuse = packed_find_computing(
        request, {'account': account, 'status': computing.models.BORROWED_KEY}, {})
    borrow = packed_find_computing(
        request, {'account': account, 'status': computing.models.VERIFYING_KEY}, {})
    ret = packed_find_computing(
        request, {
            'account': account, 'status': computing.models.RETURNING_KEY}, {})
    modif = packed_find_computing(
        request, {'account': account, 'status': computing.models.MODIFY_APPLY_KEY}, {})

    backup = packed_find_computing(
        request, {'account': account, 'status': computing.models.DESTROYING_KEY}, {})

    packs = Package.objects.all()
    pack_list = get_context_list(packs, get_pack_name)
    cont['package_list'] = pack_list

    cont['num_res_used'] = len(inuse)
    cont['num_res_borrow'] = len(borrow)
    cont['num_res_release'] = len(ret)
    cont['num_res_modif'] = len(modif)

    cont['borrowing_list'] = get_context_list(borrow, get_context_computing)
    cont['inuse_list'] = get_context_list(inuse, get_context_computing)
    cont['modifying_list'] = get_context_list(modif, get_context_computing)
    cont['returning_list'] = get_context_list(ret, get_context_computing)
    cont['backup_list'] = get_context_list(backup,get_context_computing)

    brws = packed_find_borrow(request, {'account': account}, {})
    brwing = brws.filter(status=BORROW_AUTHING_KEY)
    brw_pend = brws.filter(status=ACCEPTED_KEY)
    brw_fail = brws.filter(status=REJECTED_KEY)
    brw_inuse = brws.filter(status=BORROWED_KEY)
    reting = brws.filter(status=RETURN_AUTHING_KEY)
    ret_pend = brws.filter(status=RETURN_PENDING_KEY)

    rp_apply = brws.filter(status=REPAIR_APPLY_KEY)
    rp_pend = brws.filter(status=REPAIR_PEND_KEY)
    rping = brws.filter(status=REPAIRING_KEY)
    rped = brws.filter(status=FINISH_REPAIR_KEY)

    de_apply = brws.filter(status=DESTROY_APPLY_KEY)
    de_acp = brws.filter(status=DESTROY_ACCEPT_KEY)
    de_rej = brws.filter(status=DESTROY_REJECT_KEY)

    # OnionYST
    g_aps = packed_find_apply_goods(request, {'account': account}, {})
    g_ap_toapply = g_aps.filter(status=GOODS_APPLY_KEY)
    g_ap_apply = g_aps.filter(status=GOODS_APPLY_PEND_KEY)
    g_ap_applying = g_aps.filter(status=GOODS_APPLYING_KEY)
    g_ap_applied = g_aps.filter(status=FINISH_GOODS_APPLY_KEY)

    cont['num_goods_used'] = len(brw_inuse)
    cont['num_goods_borrow'] = len(brwing) + len(brw_pend)
    cont['num_goods_return'] = len(reting) + len(ret_pend)

    cont['goods_borrowing_list'] = get_context_list(
        brwing, get_context_userbrw)
    cont['goods_borrow_pending_list'] = get_context_list(
        brw_pend, get_context_userbrw)
    cont['goods_borrow_failed_list'] = get_context_list(
        brw_fail, get_context_userbrw)
    cont['goods_inuse_list'] = get_context_list(brw_inuse, get_context_userbrw)
    cont['goods_returning_list'] = get_context_list(
        reting, get_context_userbrw)
    cont['goods_return_pending_list'] = get_context_list(
        ret_pend, get_context_userbrw)

    cont['goods_torepair_list'] = get_context_list(
        rp_apply, get_context_userbrw)
    cont['goods_repair_list'] = get_context_list(rp_pend, get_context_userbrw)
    cont['goods_repairing_list'] = get_context_list(rping, get_context_userbrw)
    cont['goods_repaired_list'] = get_context_list(rped, get_context_userbrw)

    cont['goods_todestroy_list'] = get_context_list(
        de_apply, get_context_userbrw)
    cont['goods_destroyed_list'] = get_context_list(
        de_acp, get_context_userbrw)
    cont['goods_destroyfail_list'] = get_context_list(
        de_rej, get_context_userbrw)

    cont['goods_apply_toapply_list'] = get_context_list(
        g_ap_toapply, get_context_apply_goods)
    cont['goods_apply_apply_list'] = get_context_list(
        g_ap_apply, get_context_apply_goods)
    cont['goods_apply_applying_list'] = get_context_list(
        g_ap_applying, get_context_apply_goods)
    cont['goods_apply_applied_list'] = get_context_list(
        g_ap_applied, get_context_apply_goods)

    cont['user'] = get_context_user(request.user)
    cont['perm_list'] = request.user.get_all_permissions()

    cont['filtdata'] = False
    if 'filtdata' in request.POST:
        if request.POST['filtdata'] == 'true' or request.POST[
            'filtdata'] == 'True' or request.POST['filtdata'] == 'TRUE':
            print("true!")
            cont['filtdata'] = True

    return render(request, 'borrow.html', cont)


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def show_add_type(request):
    return render(request, "add_type.html", {
        'user': get_context_user(request.user),
    })


@method_required('GET')
@permission_required(PERM_GOODS_AUTH)
def show_manage(request):
    b_req = packed_find_borrow(request, {'status': BORROW_AUTHING_KEY}, {})
    b_pend = packed_find_borrow(request, {'status': ACCEPTED_KEY}, {})
    r_req = packed_find_borrow(request, {'status': RETURN_AUTHING_KEY}, {})
    r_pend = packed_find_borrow(request, {'status': RETURN_PENDING_KEY}, {})

    rp_apply = packed_find_borrow(request, {'status': REPAIR_APPLY_KEY}, {})
    rp_pend = packed_find_borrow(request, {'status': REPAIR_PEND_KEY}, {})
    rping = packed_find_borrow(request, {'status': REPAIRING_KEY}, {})
    rped = packed_find_borrow(request, {'status': FINISH_REPAIR_KEY}, {})

    de_apply = packed_find_borrow(request, {'status': DESTROY_APPLY_KEY}, {})

    ga_apply = packed_find_apply_goods(
        request, {'status': GOODS_APPLY_KEY}, {})
    # OnionYST
    ga_pend = packed_find_apply_goods(
        request, {'status': GOODS_APPLY_PEND_KEY}, {})
    gaing = packed_find_apply_goods(
        request, {'status': GOODS_APPLYING_KEY}, {})
    gaed = packed_find_apply_goods(
        request, {'status': FINISH_GOODS_APPLY_KEY}, {})

    b_req_list = get_context_list(b_req, get_context_borrow)
    b_pend_list = get_context_list(b_pend, get_context_borrow)
    r_req_list = get_context_list(r_req, get_context_borrow)
    r_pend_list = get_context_list(r_pend, get_context_borrow)

    rp_apply_list = get_context_list(rp_apply, get_context_borrow)
    rp_pend_list = get_context_list(rp_pend, get_context_borrow)
    rping_list = get_context_list(rping, get_context_borrow)
    rped_list = get_context_list(rped, get_context_borrow)

    de_apply_list = get_context_list(de_apply, get_context_borrow)

    ga_apply_list = get_context_list(ga_apply, get_context_apply_goods)
    # OnionYST
    ga_pend_list = get_context_list(ga_pend, get_context_apply_goods)
    gaing_list = get_context_list(gaing, get_context_apply_goods)
    gaed_list = get_context_list(gaed, get_context_apply_goods)

    # only check
    gainput = packed_find_apply_goods(
        request, {'status': INPUT_GOODS_APPLY_KEY}, {}
    )
    gainput_list = get_context_list(gainput, get_context_apply_goods)

    return render(request, 'goods_manage.html', {
        'user': get_context_user(request.user),
        'borrow_requests': b_req_list,
        'return_requests': r_req_list,
        'borrow_pending_requests': b_pend_list,
        'return_pending_requests': r_pend_list,
        'torepair_requests': rp_apply_list,
        'repair_requests': rp_pend_list,
        'repairing_requests': rping_list,
        'repaired_requests': rped_list,
        'todestroy_requests': de_apply_list,
        'togoods_apply_requests': ga_apply_list,
        'goods_apply_requests': ga_pend_list,
        'goods_applying_requests': gaing_list,
        'goods_applied_requests': gaed_list,

        # only check
        'goods_input_requests': gainput_list,

        'perm_list': request.user.get_all_permissions(),
    })


@method_required('GET')
@permission_required(PERM_VIEW_ALL)
def show_borrow_list(request):
    try:
        brw = Borrow.objects.all()
        blist = get_context_list(brw, get_context_userbrw)
        return render(request, 'log_borrow.html', {
            'user': get_context_user(request.user),
            'borrows': blist,
            'page': 1,
            'page_num': 1,
            'perm_list': request.user.get_all_permissions()
        })
    except Exception as e:
        return show_message(request, 'Error when show borrows: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_GOODS_AUTH)
def MailNotify(request):
    numberstrs = request.POST['mail-targets'].split('&')
    print(request.POST['mail-content'])
    for numberstr in numberstrs:
        try:
            itemno = int(numberstr)
            brw = Borrow.objects.get(id=itemno)
            print(brw.account)
            send_user_mail(brw.account, 'Aglaia Item Notify', request.POST['mail-content'])
        except:
            pass
    return HttpResponseRedirect(reverse("goods.views.show_list"))
