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
    list_display = ('title', 'created_on', 'updated_on')
    date_hierarchy = 'created_on'


class SegmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'file', 'track', 'start', 'end', 'playback_mode')


class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'course', 'assigner', 'assigned_on')

class SimpleCourseGroup(admin.ModelAdmin):
    list_display = ('group', 'course')

admin.site.register(models.File, FileAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Segment, SegmentAdmin)
admin.site.register(models.CourseGroup, CourseGroupAdmin)
admin.site.register(models.CourseGroupCanBeAssignedTo, SimpleCourseGroup)

# vim: set et sw=4 ts=4 sts=4 tw=78:
