from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('account.views',
                       url(r'^$', 'account_home'),
                       url(r'^signin/$', 'show_signin'),
                       url(r'^show_account/$', 'show_all_accounts'),

                       url(r'^do_signin/$', 'do_signin'),
                       url(r'^do_signup/$', 'do_signup'),
                       url(r'^do_logout/$', 'do_logout'),

                       url(r'^do_lookup_depts/$', 'do_lookup_depts'),
                       url(r'^do_verify_username/$', 'do_verify_username'),

                       url(r'^do_modify_account/$', 'do_modify_account'),
                       url(r'^do_modify_password/$', 'do_modify_password'),
                       url(r'^do_modify_email/$', 'do_modify_email'),

                       url(r'^do_approve_account/$', 'do_approve_account'),
                       url(r'^do_disapprove_account$', 'do_disapprove_account'),
                       url(r'^do_set_manager$', 'do_set_manager'),
                       url(r'^do_set_normal$', 'do_set_normal'),
                       url(r'^do_set_super$', 'do_set_super'),
                       url(r'^do_clear_manager$','do_clear_manager'),
                       url(r'^do_delete_account$','do_delete_account'),
                       url(r'^do_get_permissions$', 'do_get_permissions'),
                       url(r'^do_set_permissions$', 'do_set_permissions'),

                       url(r'^do_send_mail$', 'do_send_mail'),

                       url(r'^auth_email/(?P<username>.+)/(?P<ekey>.+)/$', 'do_auth_email')
                       )
