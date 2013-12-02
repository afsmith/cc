from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from . import models


class FileAdmin(admin.ModelAdmin):
    search_fields = ('orig_filename',)
    list_display = ('orig_filename', 'pages_num', 'created_on')
    list_filter = (
        ('created_on', DateFieldListFilter),
    )

admin.site.register(models.File, FileAdmin)
