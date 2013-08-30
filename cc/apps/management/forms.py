# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

""" Forms used by application management.
"""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.conf import settings
from django.contrib.auth import models as auth_models, authenticate
from django.utils.translation import ugettext_lazy as _
from cc.apps.management import models
from cc.apps.management.models import UserProfile

class AuthenticationForm(auth_forms.AuthenticationForm):
    username = forms.CharField(label=_("Username"), max_length=30, required=False)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username and not password:
            raise forms.ValidationError(_('Please enter a correct username and password.'))
        if not username:
            raise forms.ValidationError(_('Please enter a correct username.'))
        if not password:
            raise forms.ValidationError(_('Please enter a correct password.'))

        super(AuthenticationForm, self).clean()

    def clean_username(self):
        return self.cleaned_data['username'].strip()

    

class UserProfileForm(forms.Form):
    """Form for creating and editing user data.
    """

    GROUP_DOES_NOT_EXIST_MSG = _('Group does not exist.')

    PHONE_INVALID_MSG = _(
        'Invalid phone number. Numer must consist of '
        '+ (optional) and digits separated (or not) with single spaces.')

    ROLE_NOT_AUTH = _('You are not authorized to change roles of users.')

    group = forms.IntegerField(widget=forms.HiddenInput())
    username = forms.CharField(label=_('Username'), max_length=UserProfile.USERNAME_LENGTH)
    first_name = forms.CharField(label=_('First name'), max_length=UserProfile.FIRST_NAME_LENGTH)
    last_name = forms.CharField(label=_('Last name'), max_length=UserProfile.LAST_NAME_LENGTH)
    email = forms.EmailField(label=_('Email'))
    phone = forms.RegexField(label=_('Phone'), regex=UserProfile.PHONE_REGEX,
                             required=False,
                             max_length=20,
                             error_messages={'invalid': PHONE_INVALID_MSG})
    
    if settings.SALES_PLUS:
        choices = models.UserProfile.ROLES
    else:
        choices = [roles for roles in models.UserProfile.ROLES if roles[0] != models.UserProfile.ROLE_USER_PLUS]
        
    role = forms.TypedChoiceField(label=_('Role'), choices=choices, coerce=int)

    ocl = forms.BooleanField(label=_('OCL (One-click-link)'), required=False, initial=False, widget=forms.CheckboxInput())
    send_email = forms.BooleanField(label=_('Send message'), required=False,
                                    initial=True, widget=forms.CheckboxInput())
    #language = forms.ChoiceField(choices=settings.LANGUAGES)

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        self._admin = kwargs.pop('admin')
        super(UserProfileForm, self).__init__(*args, ** kwargs)
        if self._admin.userprofile.is_superadmin:
            self.fields['role'].choices = models.UserProfile.ROLES
        elif self._admin.userprofile.is_admin:
            self.fields['role'].choices = models.UserProfile.ROLES_CUTED
            
        if not settings.SALES_PLUS:
            self.fields['role'].choices = [roles for roles in self.fields['role'].choices \
                                            if roles[0] != models.UserProfile.ROLE_USER_PLUS]


    def clean_group(self):
        group_id = self.cleaned_data['group']
        try:
            group = auth_models.Group.objects.get(pk=group_id)
        except auth_models.Group.DoesNotExist:
            raise forms.ValidationError(self.GROUP_DOES_NOT_EXIST_MSG)
        else:
            return group

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        try:
            user = auth_models.User.objects.get(username=username)
        except auth_models.User.DoesNotExist:
            return username
        else:
            #
            # Check if there is username conflict with the user which is being
            # edited or some other user. In the first case the conflict is OK,
            # it only means that name wasn't changed.
            #
            if not self._user or (user.id != self._user.id):
                raise forms.ValidationError(
                    _('User with such username already exists. Please enter different username.')
                )
            else:
                return username

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()

    def clean_role(self):
        role = self.cleaned_data['role']
        has_role_changed = role != models.UserProfile.ROLE_USER

        #if has_role_changed and not self._is_admin_a_superadmin():
        if has_role_changed and not (self._is_admin_a_superadmin() or self._is_admin_a_admin):
            raise forms.ValidationError(self.ROLE_NOT_AUTH)
        return role

    def _is_admin_a_superadmin(self):
        return self._admin.get_profile().role == models.UserProfile.ROLE_SUPERADMIN

    def _is_admin_a_admin(self):
        return self._admin.get_profile().role == models.UserProfile.ROLE_ADMIN

    
class GroupEditForm(forms.Form):
    name = forms.CharField(label=_('Name'), min_length=4, max_length=30)

    def __init__(self, *args, **kwargs):
        self._group = kwargs.pop('group', None)
        super(GroupEditForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        try:
            group = auth_models.Group.objects.get(name=name)
        except auth_models.Group.DoesNotExist:
            return name
        else:
            #
            # Check if the name conflict is with the group which is being
            # edited or some other group. In the first case the conflict is OK,
            # it only means that name wasn't changed.
            #
            if (not self._group) or (group.id != self._group.id):
                raise forms.ValidationError(
                    _('Group with the same name already exists. Please choose different name.'))
            else:
                return name

            
class CsvImportForm(forms.Form):
    """
        Form used for importing data from CSV files.
    """
    file = forms.FileField(label=_('File'))
    send_email = forms.BooleanField(label=_('Send message'), required=False,
                                    initial=True, widget=forms.CheckboxInput())

    def clean_file(self):

        file = self.cleaned_data['file']

        filename = file.name.lower()
        if filename.rpartition('.')[2] not in models.UserImporter.SUPPORTED_FORMATS:
            raise forms.ValidationError(_('Unsupported file type.'))
        else:
            return file

class DeleteUsersFromCsvForm(CsvImportForm):
    send_goodbye_email = forms.BooleanField(label=_('Send goodbye email'), required=False, initial=False)

class ChangePasswordForm(forms.Form):
    """
        Form used to change user password.
    """

    INVALID_OLD_PASS = _('Old password is invalid.')
    DIFFERENT_NEW_PASS = _('New password must be repeated twice.')
    SAME_NEW_PASS = _('New password must be different than previous')

    user_id = forms.IntegerField(required=True,
                                 widget=forms.HiddenInput)
    old_password = forms.CharField(label=_('Old password'),
                                   required=True,
                                   widget=forms.PasswordInput)
    new_password = forms.CharField(label=_('New password'),
                                   required=True,
                                   widget=forms.PasswordInput,
                                   min_length=5,
                                   max_length=20)
    new_password_rep = forms.CharField(required=True,
                                       widget=forms.PasswordInput,
                                       min_length=5,
                                       max_length=20,
                                       label=_('Repeat new password'))

    def clean_old_password(self):
        user = auth_models.User.objects.get(pk=self.cleaned_data['user_id'])
        if not user.check_password(self.cleaned_data['old_password']):
            raise forms.ValidationError(self.INVALID_OLD_PASS)
        return self.cleaned_data['old_password']

    def validate_new_password(self):
        user = auth_models.User.objects.get(pk=self.cleaned_data['user_id'])
        if not 'new_password' in self.cleaned_data:
            raise forms.ValidationError(_('New password is required'))
        if not 'new_password_rep' in self.cleaned_data:
            raise forms.ValidationError(_('Repeat new password is required'))

        if self.cleaned_data['new_password'] != self.cleaned_data['new_password_rep']:
            raise forms.ValidationError(self.DIFFERENT_NEW_PASS)
        elif user.check_password(self.cleaned_data['new_password']):
            raise forms.ValidationError(self.SAME_NEW_PASS)

    def clean(self):
        super(ChangePasswordForm, self).clean()
        self.validate_new_password()
        return self.cleaned_data


class OCLExpirationForm(forms.Form):
    expires_on = forms.DateField(required=False)

# vim: set et sw=4 ts=4 sts=4 tw=78:
