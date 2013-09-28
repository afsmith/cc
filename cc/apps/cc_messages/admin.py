from django.contrib import admin

from . import models


class MessageAdmin(admin.ModelAdmin):
    search_fields = ('subject',)
    list_display = ('subject', 'message', 'owner')
    list_filter = ('owner', )
    date_hierarchy = 'modified_at'

admin.site.register(models.Message, MessageAdmin)
