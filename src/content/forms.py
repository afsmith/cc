# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Definitions of various forms related to content management.
"""
from __future__ import absolute_import

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from management import models as mgmnt_models

from content import models


class UserModelChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        return "%s %s" % (obj.last_name, obj.first_name)


class FileImportForm(forms.Form):
    """Form which provides interface for file uploads.
    """

    file = forms.FileField(widget=forms.FileInput(attrs={'id': 'file', 'class': 'file', 'style': "display: none;"}))

    def is_supported_file(self):
        return models.File.is_supported_file(self.cleaned_data['file'].name)


class ManageContentForm(forms.Form):
    file_id = forms.CharField(max_length=200, widget=forms.HiddenInput)
    tags_ids = forms.CharField(max_length=200, widget=forms.HiddenInput)
    language = forms.ChoiceField(label=_('Language'), choices=settings.LANGUAGES)
    title = forms.CharField(label=_('Name'), max_length=150, widget=forms.TextInput(attrs={'id': 'mct', 'style': 'width: 205px;'}))
    expires_on = forms.CharField(label=_('Expiration date'), required=False, initial='', widget=forms.TextInput(attrs={'id': 'datepicker', 'disabled': 'true'}))
    delete_expired = forms.BooleanField(label=_('Delete file after expiration'), required=False, initial=False)
    is_downloadable = forms.BooleanField(label=_('Allow downloading'), required=False, initial=True)
    duration = forms.IntegerField(label=_('Duration'), widget=forms.TextInput(attrs={}))
    note = forms.CharField(label=_('Note'), widget=forms.Textarea(attrs={'rows':'5', 'cols': '42'}))
    owner = UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) |
                                                       Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN)).
                                   order_by('last_name', 'first_name'), label=_('Owner'), empty_label=None)

    LANGUAGE_CHOICES = [
        ('', _('Unspecified'))
    ]

    def __init__(self, *args, **kwargs):
        super(ManageContentForm, self).__init__(*args, **kwargs)
        lang_choices = list(self.LANGUAGE_CHOICES)
        lang_choices.extend([(x, unicode(y)) for x, y in settings.LANGUAGES])
        self.fields['language'].choices = lang_choices

    def clean_title(self):
        return self.cleaned_data['title'].strip()


class FileFindForm(forms.Form):

    file_name = forms.CharField(max_length=150)
    file_type = forms.TypedChoiceField(choices=models.File.TYPES, coerce=int, empty_value='')
    language = forms.TypedChoiceField(choices=settings.LANGUAGES)
    tag = forms.CharField(max_length=100)
    tags_ids = forms.CharField(max_length=200, widget=forms.HiddenInput)
    page = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    from_my_groups = forms.BooleanField(label=_('My groups'), initial=True,
                                  widget=forms.CheckboxInput(attrs={'id': 'from_my_groups'}))
    my_files = forms.BooleanField(label=_('My files'),
                                  widget=forms.CheckboxInput(attrs={'id': 'my', 'checked': 'checked'}))
    inactive_files = forms.BooleanField(label=_('Inactive files'),
                                  widget=forms.CheckboxInput(attrs={'id': 'ia'}))

    CHOICES_TYPES = [
        ('', _('All types'))
    ]
    CHOICES_LANGUAGES = [
        ('', _('All languages'))
    ]

    def __init__(self, *args, **kwargs):
        super(FileFindForm, self).__init__(*args, **kwargs)
        lang_choices = list(self.CHOICES_LANGUAGES)
        lang_choices.extend([(x, unicode(y)) for x, y in settings.LANGUAGES])
        self.fields['language'].choices = lang_choices
        type_choices = list(self.CHOICES_TYPES)
        type_choices.extend([(x, unicode(y)) for x, y in models.File.TYPES])
        self.fields['file_type'].choices = type_choices


class EditModuleForm(forms.Form):
    """
        Form for module editing view.
        Provides all module's fields.
    """

    module_id = forms.CharField(max_length=200, widget=forms.HiddenInput)
    groups_ids = forms.CharField(max_length=200, widget=forms.HiddenInput)

    title = forms.CharField(label=_('Title'), max_length=150, widget=forms.TextInput(attrs={'id': 'moduleTitle'}))
    objective = forms.CharField(label=_('Module objective'), widget=forms.Textarea(attrs={'id': 'moduleObjective', 'rows':'5', 'cols': '42', 'maxlength':'2200'}))
    completion_msg = forms.CharField(label=_('Goodbye message'),
    widget=forms.Textarea(attrs={'id': 'completionMsg', 'rows':'5', 'cols': '42', 'maxlength':'2200'}), initial=_('Module complete'))
    language = forms.ChoiceField(label=_('Language'), choices=settings.LANGUAGES)
    expires_on = forms.CharField(label=_('Expiration date'), required=False, widget=forms.TextInput(attrs={'id': 'moduleDate', 'readonly': 'readonly'}))
    allow_download = forms.BooleanField(label=_('Allow downloading'), required=False, widget=forms.CheckboxInput(attrs={'id': 'allow_download'}), initial=False)
    allow_skipping = forms.BooleanField(label=_('Allow skipping'), required=False, widget=forms.CheckboxInput(attrs={'id': 'allow_skipping'}), initial=False)
    sign_off_required = forms.BooleanField(label=_('Sign off required'),
            required=False, widget=forms.CheckboxInput(attrs={'id':
                'sign_off_required'}), initial=False)

    LANGUAGE_CHOICES = [
        ('0', _('Unspecified'))
    ]

    def __init__(self, *args, **kwargs):
        super(EditModuleForm, self).__init__(*args, **kwargs)
        lang_choices = list(self.LANGUAGE_CHOICES)
        lang_choices.extend([(x, unicode(y)) for x, y in settings.LANGUAGES])
        self.fields['language'].choices = lang_choices

class SearchAssignmentsForm(forms.Form):
    language = forms.ChoiceField(label=_('Language'), choices=settings.LANGUAGES)
    owner = UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) |
                                                       Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN)).
                                   order_by('last_name', 'first_name'), empty_label=None, required=False)
    ocl = forms.BooleanField(label=_('Add one click link \'OCL\''), required=False, initial=False)
    expires_on = forms.DateField(label=_("Set expire date"),
            required=False,
            widget=forms.TextInput(attrs={'id':'id_ocl_expires_on',
                'disabled': True}))
    send_email = forms.BooleanField(label=_('Send message'), required=False,
                                    initial=True, widget=forms.CheckboxInput())

    LANGUAGE_CHOICES = [
        ('0', _('All languages'))
    ]

    def __init__(self, *args, **kwargs):
        super(SearchAssignmentsForm, self).__init__(*args, **kwargs)
        lang_choices = list(self.LANGUAGE_CHOICES)
        lang_choices.extend([(x, unicode(y)) for x, y in settings.LANGUAGES])
        self.fields['language'].choices = lang_choices

class ManageModulesForm(forms.Form):
    owner = UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) |
                                                       Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN)).
                                   order_by('last_name', 'first_name'), empty_label=None, required=False)

# vim: set et sw=4 ts=4 sts=4 tw=78:
