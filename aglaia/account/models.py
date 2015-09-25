from django.db import models
from django.contrib.auth.models import User
# from account.tests import deploy

status_unauth_key = 'u'
status_authed_key = 'a'
status_destroy_key = 'd'
status_unauth = 'unauth'
status_authed = 'auth'
status_destroy = 'deleted'

APP_NAME = 'account'
NORMAL = 'normal'
PERM_NORMAL = APP_NAME + '.' + NORMAL

GOODS_AUTH = 'goods_auth'
PERM_GOODS_AUTH = APP_NAME + '.' + GOODS_AUTH

COMPUT_AUTH = 'comput_auth'
PERM_COMPUT_AUTH = APP_NAME + '.' + COMPUT_AUTH

USER_AUTH = 'user_auth'
PERM_USER_AUTH = APP_NAME + '.' + USER_AUTH

VIEW_ALL = 'view_all'
PERM_VIEW_ALL = APP_NAME + '.' + VIEW_ALL

MODF_NORMAL = 'modf_normal'
PERM_MODF_NORMAL = APP_NAME + '.' + MODF_NORMAL

MODF_KEY = 'modf_key'
PERM_MODF_KEY = APP_NAME + '.' + MODF_KEY

MODF_PERM = 'modf_perm'
PERM_MODF_PERM = APP_NAME + '.' + MODF_PERM

MODF_GROUP = 'modf_group'
PERM_MODF_GROUP = APP_NAME + '.' + MODF_GROUP

DEL_USER = 'del_user'
PERM_DEL_USER = APP_NAME + '.' + DEL_USER


class Department(models.Model):
    depart_name = models.CharField(max_length=100)  # wait for modify

    def __str__(self):
        return str(self.depart_name)


class Account(models.Model):
    status_CHOICES = (
        (status_unauth_key, status_unauth),
        (status_authed_key, status_authed),
        (status_destroy_key, status_destroy)
    )

    class Meta:
        permissions = ((NORMAL, '普通借用'),
                       (GOODS_AUTH, '实物添加、删除、借用审核'),
                       (COMPUT_AUTH, '计算资源借用审核'),
                       (USER_AUTH, '用户身份审核'),
                       (VIEW_ALL, '查看所有用户和日志'),
                       (MODF_NORMAL, '修改他人的普通信息'),
                       (MODF_KEY, '修改所有人的敏感信息'),
                       (MODF_PERM, '修改所有人的权限信息'),
                       (MODF_GROUP, '修改所有人所在的用户组'),
                       (DEL_USER, '删除用户'))

    real_name = models.CharField(max_length=50)
    department = models.ManyToManyField(Department, blank=True)
    tel = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=3, choices=status_CHOICES)
    user = models.OneToOneField(User)
    school_id = models.CharField(max_length=30, default='1234567890')
    email_auth = models.BooleanField(blank=True, default=False)
    email_hash = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return str(self.user.username)
