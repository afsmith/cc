# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

"""URL dispatcher configuration for the app.
"""

from django.conf.urls.defaults import *

from assignments import views


urlpatterns = patterns('',
    url(r'^group/modules/$', views.group_modules, name='assignments-group_modules'),
    url(r'^user/modules/$', views.user_modules, name='assignments-user_modules'),
    url(r'^user/progress/$', views.user_progress, name='assignments-user_progress'),
    url(r'^module/progress/$', views.module_progress, name='assignments-module_progress'),
    url(r'^users_per_module/$', views.users_per_module, name='assignments-users_per_module'),
    url(r'^published_modules/$', views.published_modules, name='assignments-published_modules'),
    url(r'^group_status/(?P<group_id>\d+)$', views.group_status, name='assignments-group_status'),
)


# vim: set et sw=4 ts=4 sts=4 tw=78:

  
