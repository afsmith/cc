from django.contrib import admin
from django.contrib.auth.models import Group

from . import models


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

    def user_type(self, obj):
        if obj.country == 'N/A':
            return 'Recipient'
        else:
            return 'Sender'

admin.site.register(models.CUser, UserAdmin)

# Hide the Group panel for now
admin.site.unregister(Group)
