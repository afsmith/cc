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
from cc.apps.tracking import models


class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('segment', 'participant', 'created_on', 'event_type')


admin.site.register(models.TrackingEvent, TrackingEventAdmin)


# vim: set et sw=4 ts=4 sts=4 tw=78:
