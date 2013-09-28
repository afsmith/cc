from django.contrib import admin
from cc.apps.content import models


class FileAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'type', 'status')
    list_filter = ('status', 'type')
    date_hierarchy = 'updated_on'

admin.site.register(models.File, FileAdmin)
