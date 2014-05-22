from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from . import models


class MessageAdmin(admin.ModelAdmin):
    search_fields = ('subject',)
    list_display = (
        'subject', 'message', 'owner',
        'cc_me', 'allow_download', 'created_at'
    )
    list_filter = (
        'owner',
        ('created_at', DateFieldListFilter)
    )
    date_hierarchy = 'modified_at'

admin.site.register(models.Message, MessageAdmin)
