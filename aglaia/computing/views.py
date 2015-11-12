# -*- coding: utf-8 -*-
from aglaia.mail_tools import *

from account.views import get_context_user
from computing.interface import *
from aglaia.message_center import Message


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================

def get_context_computing(comp):
    dc = {}
    dc['id'] = comp.id
    dc['name'] = comp.name
    dc['status'] = comp.get_status_display()
    dc['package_name'] = comp.pack_name
    dc['type'] = comp.get_pc_type_display()
    dc['cpu'] = comp.cpu
    dc['memory'] = comp.memory
    dc['disk'] = comp.disk
    dc['disktype'] = comp.get_disk_type_display()
    dc['ip'] = comp.address
    dc['os'] = comp.os
    dc['login'] = comp.login
    dc['initial_password'] = comp.password
    # dc['expire_time'] = comp.expire_time.strftime('%Y-%m-%d')
    dc['name'] = comp.account.real_name
    dc['flag'] = comp.flag
    dc['sn'] = comp.sn
    dc['data_content'] = comp.data_content
    dc['note'] = Message(comp.note).last()['text']
    return dc


def get_context_server(sv):
    dc = {}
    dc['id'] = sv.id
    dc['name'] = sv.name
    dc['status'] = sv.get_status_display()
    dc['account_num'] = '0'
    return dc


def get_context_pack(pa):
    dc = {}
    dc['name'] = pa.name
    dc['type'] = pa.get_pc_type_display()
    dc['cpu'] = pa.cpu
    dc['memory'] = pa.memory
    dc['disktype'] = pa.get_disk_type_display()
    dc['disk'] = pa.disk
    dc['os'] = pa.os
    return dc


def get_pack_prop(dc, p_nm):
    p = Package.objects.get(name=p_nm)
    dc['pc_type'] = p.pc_type
    dc['cpu'] = p.cpu
    dc['memory'] = p.memory
    dc['disk'] = p.disk
    dc['pack_name'] = p_nm
    if p.disk_type == SSD_KEY:
        dc['disk_type'] = 'SSD'
    else:
        dc['disk_type'] = 'HDD'
    dc['os'] = p.os


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================

@method_required('POST')
@permission_required(PERM_NORMAL, http_denied)
def do_borrow_request(request):
    post = request.POST
    comp = {}
    try:
        p_nm = no_excp_post(request, 'package')
        if p_nm != 'none':
            get_pack_prop(comp, p_nm)
        else:
            if post['type'] == 'real':
                comp['pc_type'] = PHYSICAL_MACHINE_KEY
            else:
                comp['pc_type'] = VIRTUAL_MACHINE_KEY
            comp['cpu'] = post['cpu']
            comp['memory'] = post['memory']
            comp['disk'] = post['disk']
            if post['disk_type'] == 'SSD':
                comp['disk_type'] = SSD_KEY
            else:
                comp['disk_type'] = MACHINE_KEY
            comp['os'] = post['os']
            comp['pack_name'] = 'user_defined'
        comp['expire_time'] = datetime.now()
        comp['login'] = post['login']
        comp['password'] = post['initial_password']
        comp['status'] = VERIFYING_KEY
        comp['account'] = Account.objects.get(user=request.user)
        comp['address'] = UNKNOWN_ADDR
        comp['note'] = post['reason']
        comp['flag'] = post['flag']
        comp['data_content'] = post['data_content']

        if comp['note'] == '':
            comp['note'] = get_comp_request_log()
        message = Message()
        message.append({'direction': 'Recv',
                        'info_type': '',
                        'user_name': request.user.username,
                        'text': comp['note']})
        comp['note'] = message.tostring()

        if 'name' in post:
            comp['name'] = post['name']
        else:
            comp['name'] = ''
        c = packed_create_computing(
            request, [comp], log=get_comp_request_log())
        send_notify_mail(request, CompRequestMail, comp=c[0])
        return HttpResponse('ok')
    except Exception as e:
        return HttpResponse('denied')


@method_required('POST')
@permission_required(PERM_NORMAL, http_denied)
def do_return_request(request):
    try:
        id = request.POST['id']
        comp = Computing.objects.get(id=id)
        if not (comp.status == DESTROYING_KEY or comp.status ==
                BORROWED_KEY or comp.status == MODIFY_APPLY_KEY):
            return HttpResponse('denied')
        packed_update_computing(
            request, id, {
                'status': RETURNING_KEY}, log=get_comp_ret_log())
        send_notify_mail(request, CompReturnMail, comp=comp)
        return HttpResponseRedirect(reverse('goods.views.show_borrow'))
    #		return HttpResponse('ok')
    except:
        return HttpResponse('denied')


@method_required('POST')
@permission_required(PERM_NORMAL, http_denied)
def do_modif_request(request):
    try:
        post = request.POST
        id = post['id']
        comp = Computing.objects.get(id=id)
        if not comp.status == BORROWED_KEY:
            return HttpResponse('denied')

        if post['reason'] == '':
            post['reason'] = get_comp_modif_log()
        message = Message(comp.note)
        message.append({'direction': 'Recv',
                        'info_type': '',
                        'user_name': request.user.username,
                        'text': post['reason']})
        post['reason'] = message.tostring()

        packed_update_computing(request, id, {'status': MODIFY_APPLY_KEY, 'note': post[
            'reason']}, log=get_comp_modif_log())
        send_notify_mail(request, CompModfApplyMail, comp=comp)

        return HttpResponse('ok')
    except:
        return HttpResponse('denied')


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_approve_borrow(request):
    try:
        post = request.POST
        id = post['id']
        comp = Computing.objects.get(id=id)
        login = post['login']
        pw = post['initial_password']
        note = post['note']
        sn = post['sn']
        addr = post['ip']
        if not comp.status == VERIFYING_KEY:
            return show_denied_message(request)

        if note == '':
            note = get_comp_approve_log()
        message = Message(comp.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})
        note = message.tostring()

        packed_update_computing(request, id,
                                {'status': BORROWED_KEY,
                                 'note': note,
                                 'sn': sn,
                                 'login': login,
                                 'password': pw,
                                 'address': addr}, log=get_comp_approve_log())

        send_notify_mail(request, CompApproveMail, comp=comp)

        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Something wrong when approve computing resource: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_disapprove_borrow(request):
    try:
        post = request.POST
        id = post['id']
        note = post['note']
        comp = Computing.objects.get(id=id)
        if not comp.status == VERIFYING_KEY:
            return show_denied_message(request)

        if note == '':
            note = get_comp_disap_log()
        message = Message(comp.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})
        note = message.tostring()

        packed_update_computing(
            request, id, {
                'status': VERIFY_FAIL_KEY, 'note': note}, log=get_comp_disap_log())
        send_notify_mail(request, CompDisapproveMail, comp=comp)

        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Something wrong when disapprove computing resource: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_approve_return(request):
    try:
        post = request.POST
        id = post['id']
        note = post['note']
        comp = Computing.objects.get(id=id)
        if not comp.status == RETURNING_KEY:
            return show_denied_message(request)

        if note == '':
            note = get_comp_reted_log()
        message = Message(comp.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})
        note = message.tostring()

        packed_update_computing(
            request, id, {
                'status': RETURNED_KEY, 'note': note}, log=get_comp_reted_log())
        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Something wrong when approve return: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_approve_modify(request):
    try:
        post = request.POST
        id = post['id']
        comp = Computing.objects.get(id=id)
        if not comp.status == MODIFY_APPLY_KEY:
            return show_denied_message(request)

        if post['note'] == '':
            post['note'] = get_comp_modfed_log()
        message = Message(comp.note)
        message.append({'direction': 'Send',
                        'info_type': '',
                        'user_name': request.user.username,
                        'text': post['note']})
        post['note'] = message.tostring()

        dic = {}
        dic['status'] = BORROWED_KEY
        dic['note'] = post['note']
        if post['type'] == 'real':
            dic['pc_type'] = PHYSICAL_MACHINE_KEY
        else:
            dic['pc_type'] = VIRTUAL_MACHINE_KEY

        if post['disktype'] == 'SSD':
            dic['disk_type'] = SSD_KEY
        else:
            dic['disk_type'] = MACHINE_KEY
        dic['cpu'] = post['cpu']
        dic['memory'] = post['memory']
        dic['disk'] = post['disk']
        dic['address'] = post['ip']
        dic['os'] = post['os']
        dic['data_content'] = post['data_content']
        # dic['login'] = post['login']
        # dic['password'] = post['initial_password']

        packed_update_computing(request, id, dic, log=get_comp_modfed_log())
        send_notify_mail(request, CompModfedMail, comp=comp)

        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Something wrong when approve modify: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_disapprove_modify(request):
    try:
        post = request.POST
        id = post['id']
        note = post['note']
        comp = Computing.objects.get(id=id)
        if not comp.status == MODIFY_APPLY_KEY:
            return show_denied_message(request)

        if note == '':
            note = get_comp_rej_modf_log()
        message = Message(comp.note)
        message.append({'direction': 'Send', 'info_type': '',
                        'user_name': request.user.username, 'text': note})
        note = message.tostring()

        packed_update_computing(
            request, id, {
                'status': BORROWED_KEY, 'note': note}, log=get_comp_rej_modf_log())
        send_notify_mail(request, CompRejectModfMail, comp=comp)

        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Something wrong when disapprove modify: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_create_package(request):
    try:
        post = request.POST
        dc = {}
        dc['name'] = post['name']
        dc['cpu'] = post['cpu']
        dc['memory'] = post['memory']
        dc['disk'] = post['disk']
        dc['os'] = post['os']
        if post['type'] == 'real':
            dc['pc_type'] = PHYSICAL_MACHINE_KEY
        else:
            dc['pc_type'] = VIRTUAL_MACHINE_KEY
        if post['disktype'] == 'SSD':
            dc['disk_type'] = SSD_KEY
        else:
            dc['disk_type'] = MACHINE_KEY
        packed_create_package(request, dc)
        return HttpResponseRedirect(
            reverse('computing.views.show_comp_manage'))
    except Exception as e:
        return show_message(request, 'Creating package failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_delete_package(request):
    try:
        post = request.POST
        nm = post['name']
        pk = Package.objects.get(name=nm)
        packed_delete_package(request, pk.id)
        return HttpResponseRedirect(
            reverse('computing.views.show_comp_manage'))
    except Exception as e:
        return show_message(request, 'Delete package failed: ' + e.__str__())


@method_required('POST')
@login_required
def do_get_package(request):
    try:
        nm = request.POST['name']
        p = Package.objects.get(name=nm)
        d = get_context_pack(p)
        return HttpResponse(json.dumps(d))
    except Exception as e:
        return HttpResponse('Failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_NORMAL)
def do_set_flag(request):
    try:
        id = request.POST['id']
        flag = None
        if request.POST['flag'] == 'false':
            flag = False
        else:
            flag = True
        comp = Computing.objects.get(id=id)
        if not comp.account.user == request.user:
            return show_message(
                request, 'This resource is not borrowed by you!')
        if request.POST['flag'] == 'true':
            packed_update_computing(
                request, id, {
                    'flag': flag, 'data_content': request.POST['content']})
        else:
            packed_update_computing(
                request, id, {
                    'status': BORROWED_KEY, 'flag': flag})
            comp = Computing.objects.get(id=id)
        return HttpResponseRedirect(reverse('goods.views.show_borrow'))
    except Exception as e:
        return show_message(request, 'Set flag failed: ' + e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH, json_denied)
def do_get_comp_prop(request):
    try:
        id = request.POST['id']
        comp = Computing.objects.get(id=id)
        dc = get_context_computing(comp)
        dc['retcode'] = 'ok'
        return HttpResponse(json.dumps(dc))
    except Exception as e:
        print(e)
        return json_denied(request)


# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================
# ===============================================

@method_required('GET')
@permission_required(PERM_COMPUT_AUTH)
def show_comp_verify(request):
    inuse = packed_find_computing(request, {'status': BORROWED_KEY}, {})
    borrow = packed_find_computing(request, {'status': VERIFYING_KEY}, {})
    ret = packed_find_computing(request, {'status': RETURNING_KEY}, {})
    modif = packed_find_computing(request, {'status': MODIFY_APPLY_KEY}, {})
    backup = packed_find_computing(request, {'status': DESTROYING_KEY}, {})

    packs = Package.objects.all()
    cont = {}
    cont['curpage'] = 'comp_verify'

    b_list = get_context_list(borrow, get_context_computing)
    cont['borrowing_list'] = b_list
    cont['borrowing_num'] = len(b_list)

    u_list = get_context_list(inuse, get_context_computing)
    cont['inuse_list'] = u_list
    cont['inuse_num'] = len(u_list)

    m_list = get_context_list(modif, get_context_computing)
    cont['modifying_list'] = m_list
    cont['modifying_num'] = len(m_list)

    r_list = get_context_list(ret, get_context_computing)
    cont['returning_list'] = r_list
    cont['returning_num'] = len(r_list)

    user = get_context_user(request.user)
    cont['user'] = user
    cont['perm_list'] = request.user.get_all_permissions()

    backup_list = get_context_list(backup, get_context_computing)
    cont['backup_list'] = backup_list
    cont['backup_num'] = len(backup_list)

    return render(request, 'calc_verify.html', cont)


def show_comp_manage(request):
    packs = Package.objects.all()
    cont = {}
    cont['curpage'] = 'comp_manage'

    pack_list = get_context_list(packs, get_context_pack)
    cont['package_list'] = pack_list
    cont['package_num'] = len(pack_list)

    user = get_context_user(request.user)
    cont['user'] = user
    cont['perm_list'] = request.user.get_all_permissions()

    return render(request, 'calc_manage.html', cont)

#
# @method_required('GET')
# @permission_required(PERM_COMPUT_AUTH)
# def show_calc_resource(request):
#     inuse = packed_find_computing(request, {'status': BORROWED_KEY}, {})
#     borrow = packed_find_computing(request, {'status': VERIFYING_KEY}, {})
#     ret = packed_find_computing(request, {'status': RETURNING_KEY}, {})
#     modif = packed_find_computing(request, {'status': MODIFY_APPLY_KEY}, {})
#
#     packs = Package.objects.all()
#     cont = {}
#
#     pack_list = get_context_list(packs, get_context_pack)
#     cont['package_list'] = pack_list
#     cont['package_num'] = len(pack_list)
#
#     b_list = get_context_list(borrow, get_context_computing)
#     cont['borrowing_list'] = b_list
#     cont['borrowing_num'] = len(b_list)
#
#     u_list = get_context_list(inuse, get_context_computing)
#     cont['inuse_list'] = u_list
#     cont['inuse_num'] = len(u_list)
#
#     m_list = get_context_list(modif, get_context_computing)
#     cont['modifying_list'] = m_list
#     cont['modifying_num'] = len(m_list)
#
#     r_list = get_context_list(ret, get_context_computing)
#     cont['returning_list'] = r_list
#     cont['returning_num'] = len(r_list)
#
#     user = get_context_user(request.user)
#     cont['user'] = user
#     cont['perm_list'] = request.user.get_all_permissions()
#
#     return render(request, 'calc_resource.html', cont)


@method_required('GET')
@permission_required(PERM_VIEW_ALL)
def show_computing_list(request):
    try:
        comp = Computing.objects.all()
        clist = get_context_list(comp, get_context_computing)
        perm_list = request.user.get_all_permissions()
        return render(request, 'log_computing.html', {
            'user': get_context_user(request.user),
            'computings': clist,
            'page': 1,
            'page_num': 1,
            "perm_list": perm_list
        })
    except Exception as e:
        return show_message(
            request,
            'Error when show computings: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_destroyed_comp(request):
    try:
        post = request.POST
        id = post['id']
        comp = Computing.objects.get(id=id)
        message = Message(comp.note)
        message.append({'direction': 'Recv',
                        'info_type': '',
                        'user_name': request.user.username,
                        'text': get_comp_destroyed_log()})
        note = message.tostring()
        packed_update_computing(request, id, {
            'status': DESTROYED_KEY,'note':note}, log=get_comp_destroyed_log())
        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Destroy computing failed: ' +
            e.__str__())


@method_required('POST')
@permission_required(PERM_COMPUT_AUTH)
def do_destroying_comp(request):
    try:
        post = request.POST
        id = post['id']
        comp = Computing.objects.get(id=id)
        message = Message(comp.note)
        message.append({'direction': 'Recv',
                        'info_type': '',
                        'user_name': request.user.username,
                        'text': get_comp_destroying_log()})
        note = message.tostring()
        packed_update_computing(request, id, {
            'status': DESTROYING_KEY,'note':note}, log=get_comp_destroying_log())
        send_user_mail(
            comp.account,
            'Aglaia Item Notify',
            get_comp_destroying_mail())
        return HttpResponseRedirect(
            reverse('computing.views.show_comp_verify'))
    except Exception as e:
        return show_message(
            request,
            'Destroy computing failed: ' +
            e.__str__())
