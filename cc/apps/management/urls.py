# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""URL dispatcher configuration for the app.
"""

from django.conf.urls.defaults import *
from django.conf import settings

from cc.apps.management import views


urlpatterns = patterns('',
    url(r'^users/$', views.users, name='management-users'),
    url(r'^users/list/$', views.list_users, name='management-list_users'),
    url(r'^users/validate_form/$', views.user_form_validator, name='management-user_form_validator'),
    url(r'^users/create/$', views.create_user, name='management-create_user'),
#    url(r'^users/profile/$', views.user_profile, name='management-user_profile'),
    url(r'^users/password/$', views.user_password_change, name='management-user_password'),
    url(r'^users/(?P<id>\d+)/delete/$',views.delete_user, name='management-delete_user'),
    url(r'^users/delete/$',views.delete_users_from_csv, name='management-delete_users_from_csv'),
    url(r'^users/(?P<id>\d+)/$', views.edit_user, name='management-edit_user'),
    url(r'^users/(?P<id>\d+)/activate/$', views.activate_user, name='management-activate_user'),
    url(r'^users/(?P<id>\d+)/deactivate/$', views.deactivate_user, name='management-deactivate_user'),
    url(r'^users/(?P<id>\d+)/reset_pass/$', views.reset_password, name='management-reset_password'),
    url(r'^users/(?P<id>\d+)/groups/$', views.user_groups, name='management-user_groups'),
    url(r'^users/(?P<user_id>\d+)/(?P<group_id>\d+)/$', views.toggle_group_manager, name='management-toggle_manager'),
    url(r'^ocl/(?P<id>\d+)/expire/$', views.ocl_expire, name='management-ocl_expire'),
    url(r'^groups/create/$', views.create_group, name='management-create_group'),
    url(r'^groups/(?P<id>\d+)/delete/$', views.delete_group, name='management-delete_group'),
    url(r'^groups/(?P<id>-?\d+)/users/$', views.group_users, name='management-group_users'),
    url(r'^groups/list/$', views.groups_list, name='management-groups_list'),
    url(r'^groups/(?P<id>\d+)/$', views.edit_group, name='management-edit_group'),
    url(r'^groups/(?P<group_id>\d+)/members/$', views.memberships, name='management-memberships'),
    url(r'^groups/(?P<group_id>\d+)/members/export/$', views.export_users, name='management-export_users'),
    url(r'^groups/(?P<group_id>\d+)/members/import/$', views.import_users, name='management-import_users'),
    url(r'^groups/selfregister/$',
        views.groups_self_register, name='management-self_register_groups'),
    url(r'^admin_modules/$', views.admin_modules, name='management-admin_modules')
)

if settings.STATUS_CHECKBOX:
    urlpatterns += patterns('', url(r'^users/(?P<id>\d+)/has_card/$', views.toggle_has_card, name='management-toggle_has_card'))


# vim: set et sw=4 ts=4 sts=4 tw=78:
