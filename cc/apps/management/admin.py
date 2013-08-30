# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#
#

"""Configuration of the admin app.
"""

from django.contrib import admin

from cc.apps.management import models


class UserGroupProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'access_level')
    search_fields = ('user', 'group')
    ordering = ('user',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role',)
    search_fields = ('user',)
    ordering = ('user',)

class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ('group', 'self_register_enabled',)
    search_fields = ('group',)
    ordering = ('group',)


admin.site.register(models.UserGroupProfile, UserGroupProfileAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.GroupProfile, GroupProfileAdmin)


# vim: set et sw=4 ts=4 sts=4 tw=78:
