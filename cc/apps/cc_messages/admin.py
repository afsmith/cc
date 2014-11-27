from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from . import models


class MessageAdmin(admin.ModelAdmin):
    search_fields = ['subject', 'owner__email']
    list_display = (
        'subject', 'owner',
        'cc_me', 'allow_download', 'created_at'
    )
    list_filter = (
        ('created_at', DateFieldListFilter),
    )
    date_hierarchy = 'modified_at'

admin.site.register(models.Message, MessageAdmin)
