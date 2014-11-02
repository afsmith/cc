from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponse

from . import models
from cc.apps.cc_messages.models import Message

import csv


class UserTypeListFilter(admin.SimpleListFilter):
    title = 'user type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('sender', 'Sender'),
            ('recipient', 'Recipient'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sender':
            return queryset.exclude(country='N/A')
        if self.value() == 'recipient':
            return queryset.filter(country='N/A')


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'first_name', 'last_name')
    list_display = (
        'email', 'first_name', 'last_name',
        'is_active', 'user_type', 'date_joined', 'last_login'
    )
    list_filter = (UserTypeListFilter, 'is_active')
    ordering = ('-date_joined', 'last_login')
    actions = [
        'export_report'
    ]

    def user_type(self, obj):
        if obj.country == 'N/A':
            return 'Recipient'
        else:
            return 'Sender'

    def export_report(self, request, queryset):
        '''
        Sender's address, receivers' addresses and message token
        '''
        # prepare CSV response
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'
        writer = csv.writer(response, delimiter=',', quotechar='"')

        # Write a first row with header information
        field_names = ['Sender', 'Recipient', 'Subject']
        writer.writerow(field_names)

        # get all messages belong to this users, take sender only
        messages = Message.objects.filter(
            owner__in=queryset.exclude(country='N/A')
        ).order_by('owner', 'created_at')

        # loop through all recipients and write each row
        for msg in messages:
            for recipient in msg.receivers.all():
                writer.writerow([
                    msg.owner.email,
                    recipient.email,
                    unicode(msg.subject).encode('utf-8')
                ])
        return response
    export_report.short_description = 'Export user sending report'


admin.site.register(models.CUser, UserAdmin)

# Hide the Group panel for now
admin.site.unregister(Group)
