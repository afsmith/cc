# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""URL dispatcher configuration for the app.
"""

from django.conf.urls.defaults import *

from content import views


urlpatterns = patterns('',
    url(r'^$', views.manage_modules, name='content-manage_modules'),
    url(r'^copy/(?P<id>\d+)/$', views.copy_module, name='content-copy_module'),
    url(r'^create/$', views.create_module, name='content-create_module'),
    url(r'^create/(?P<id>\d+)/$', views.create_module, name='content-edit_module'),
    url(r'^save/$', views.save_module, name='content-save_module'),
    url(r'^files/$', views.find_files, name='content-find_files'),
    url(r'^manage/$', views.files_manage, name='content-files_manage'),
    url(r'^manage/(?P<file_id>\d+)/$', views.edit_content, name='content-edit_content'),
    url(r'^manage/(?P<file_id>\d+)/delete/$', views.delete_content, name='content-delete_content'),
    url(r'^manage/save/$', views.save_manage_content, name='content-save_manage_content'),
    url(r'^modules/assign/$', views.assign_module, name='content-assign_module'),
    url(r'^modules/preview_assignment/$', views.preview_assignment, name='content-preview_assignment'),
    url(r'^modules/list/$', views.modules_list, name='content-modules_list'),
    url(r'^modules/active/list/$', views.active_modules_list, name='content-active_modules_list'),
    url(r'^modules/(?P<id>\d+)/$', views.module_descr, name='content-module_descr'),
    url(r'^modules/(?P<id>\d+)/state/$', views.change_state, name='content-module_change_state'),
    url(r'^import/$', views.import_file, name='content-import_file'),
    url(r'^dms/$', views.choose_file_from_dms, name='content-dms'),
    url(r'^dms/files/$', views.dms_files, name='content-dms_files'),
    url(r'^view_smm/(?P<id>\d+)/$', views.view_module_smm, name='content-view_module_smm'),
    url(r'^view/(?P<id>\d+)/$', views.view_module, name='content-view_module'),
    url(r'^sign-off/(?P<id>\d+)/$', views.sign_off_module, name='content-sign_off_module'),
    url(r'^show-sign-off-button/(?P<id>\d+)/$', views.show_sign_off_button, name='content-show_sign_off_button'),
    url(r'^file/(?P<id>.*)/$', views.file_source, name='content-file_source'),
    url(r'^file/(?P<file_id>\d+)/download/$', views.download_file, name='content-file_downlod'),
    url(r'^files_number/$', views.files_number, name='content-files_number'),
    url(r'^collections/$', views.list_collections, name='content-collections_list'),
    url(r'^collections/save/$', views.create_collection, name='content-collections_create'),
    url(r'^collections/save/(?P<id>\d+)/$', views.save_collection, name='content-collections_save'),
    url(r'^collections/delete/(?P<id>\d+)/$', views.delete_collection, name='content-collections_delete'),
    url(r'^segment/(?P<id>\d+)/$', views.load_by_segment, name='load-segment'),
    url(r'^segment/(?P<segment_id>\d+)/download/$', views.download_segment, name='content-segment_downlod'),
    url(r'^rss/$', views.rss_feeds_list, name='content-group-modules-feed-list'),
    url(r'^rss/(?P<group_id>\d+)/$', views.AssignedModulesFeed(), name='content-group-modules-feed'),
)


# vim: set et sw=4 ts=4 sts=4 tw=78:
