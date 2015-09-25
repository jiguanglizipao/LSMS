
def get_accept_brw_log(*args, **kwargs):
    return '同意借用'

def get_reject_brw_log(*args, **kwargs):
    return '拒绝借用'

def get_finish_brw_log(*args, **kwargs):
    return '确认物品被取走'

def get_good_brwed_log(*args, **kwargs):
    return '确认被借用'

def get_accept_ret_log(*args, **kwargs):
    return '同意归还'

def get_lost_ret_log(*args, **kwargs):
    return '确认遗失'

def get_good_lost_log(*args, **kwargs):
    return '确认遗失'

def get_good_reted_log(*args, **kwargs):
    return '归还入库'

def get_brw_reted_log(*args, **kwargs):
    return '确认归还'

def get_good_dmg_log():
    return '确认损坏'

def get_brw_dmg_log():
    return '物品损坏'

def get_good_unvail_log(*args, **kwargs):
    return '置为不可用'

def get_brw_requst_log(*args, **kwargs):
    return '提出借用申请'

def get_good_avail_log(*args, **kwargs):
    return '置为可用'

def get_good_destroy_log(*args, **kwargs):
    return '销毁'

def get_ret_request_log(*args, **kwargs):
    return '提出归还申请'

def get_miss_request_log(*args, **kwargs):
    return '提出挂失申请'

def get_repair_apply_log(*args, **kwargs):
    return '提出维修申请'

def get_accept_repair_log(*args, **kwargs):
    return '同意维修申请'

def get_reject_repair_log(*args, **kwargs):
    return '拒绝维修申请'

def get_brw_repairing_log(*args, **kwargs):
    return '物品进入维修状态'

def get_good_repairing_log(*args, **kwargs):
    return '进入维修状态'

def get_finish_repair_log(*args, **kwargs):
    return '维修完毕'

def get_ret_repaired_log(*args, **kwargs):
    return '维修完的物品被取回'

def get_good_repaired_log(*args, **kwargs):
    return '维修完毕'

def get_account_modif_log(*args, **kwargs):
    return '修改账户信息'

def get_pass_modif_log(*args, **kwargs):
    return '修改账户密码'

def get_email_modif_log(*args, **kwargs):
    return '修改邮箱'

def get_approve_account_log(*args, **kwargs):
    return '用户身份认定，审核通过'

def get_delete_account_log(*args, **kwargs):
    return '销毁用户'

def get_disapprove_account_log(*args, **kwargs):
    return '取消用户身份认定'

def get_comp_request_log(*args, **kwargs):
    return '提交资源借用申请'

def get_comp_ret_log(*args, **kwargs):
    return '提交资源释放申请'

def get_comp_modif_log(*args, **kwargs):
    return '提交资源配置修改申请'

def get_comp_approve_log(*args, **kwargs):
    return '同意借出资源'

def get_comp_disap_log(*args, **kwargs):
    return '拒绝借出资源'

def get_comp_reted_log(*args, **kwargs):
    return '资源释放完毕'

def get_comp_modfed_log(*args, **kwargs):
    return '资源配置修改完毕'

def get_comp_rej_modf_log(*args, **kwargs):
    return '拒绝修改资源配置'

def get_set_manager_log(*args, **kwargs):
    return '设置为管理员，并给予相关权限'

def get_rm_manager_log(*args, **kwargs):
    return '取消管理员，并取消相关权限'

def get_wrong_goods_status_log(*args, **kwargs):
    return '物品状态错误，将请求重置为待审核状态'

def get_set_perm_log(perms, perm_set):
    return '手动设置权限：' + perm_set.__str__()


