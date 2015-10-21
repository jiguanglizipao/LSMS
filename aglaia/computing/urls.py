from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('computing.views',
                       url(r'^do_modif_request/$', 'do_modif_request'),
                       url(r'^do_borrow_request/$', 'do_borrow_request'),
                       url(r'^do_return_request/$', 'do_return_request'),
                       url(r'^do_approve_borrow$', 'do_approve_borrow'),
                       url(r'^do_approve_return$', 'do_approve_return'),
                       url(r'^do_disapprove_borrow$', 'do_disapprove_borrow'),
                       url(r'^do_approve_modify$', 'do_approve_modify'),
                       url(r'^do_disapprove_modify$', 'do_disapprove_modify'),
                       url(r'^do_create_package$', 'do_create_package'),
                       url(r'^do_delete_package$', 'do_delete_package'),
                       url(r'^do_get_package$', 'do_get_package'),
                       url(r'^do_get_comp_prop$', 'do_get_comp_prop'),
                       url(r'^do_set_flag$', 'do_set_flag'),
                       url(r'^do_destroy_comp$', 'do_destroy_comp'),
                       url(r'^show_computing_list$', 'show_computing_list'),
                       url(r'^show_comp_verify/$', 'show_comp_verify')
                       )
