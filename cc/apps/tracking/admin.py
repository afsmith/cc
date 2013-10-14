from django.contrib import admin
from cc.apps.tracking import models


class TrackingSessionAdmin(admin.ModelAdmin):
    list_display = ('message', 'participant', 'created_at')


admin.site.register(models.TrackingSession, TrackingSessionAdmin)
