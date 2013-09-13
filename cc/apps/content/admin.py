# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Configuration of the admin application.
"""


from django.contrib import admin
from cc.apps.content import models


class FileAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'type', 'status')
    list_filter = ('status', 'type')
    date_hierarchy = 'updated_on'


class CourseAdmin(admin.ModelAdmin):
    search_fields = ('title', 'objective')
    list_display = ('title', 'created_at', 'modified_at')
    date_hierarchy = 'created_at'

admin.site.register(models.File, FileAdmin)
admin.site.register(models.Course, CourseAdmin)
