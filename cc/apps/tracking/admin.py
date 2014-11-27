from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from . import models


class TrackingLogAdmin(admin.ModelAdmin):
    search_fields = ['message__subject', 'participant__email', 'action']
    list_display = ('message', 'participant', 'action', 'created_at')
    list_filter = (
        'action',
        ('created_at', DateFieldListFilter),
    )

admin.site.register(models.TrackingLog, TrackingLogAdmin)
