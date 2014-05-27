from django import forms
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import Message
from cc.apps.content.models import File
from cc.apps.accounts.models import CUser

import re
from datetime import timedelta


class MessageForm(forms.ModelForm):
    to = forms.CharField()
    signature = forms.CharField(required=False)
    attachment = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Message
        fields = [
            'subject',
            'cc_me',
            'allow_download',
            'message',
        ]
        exclude = ['receivers', 'owner', 'files']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
            'allow_download': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        # manually order the fields
        self.fields.keyOrder = [
            'to',
            'subject',
            'cc_me',
            'message',
            'signature',

            # hidden
            'attachment',
            'allow_download',
        ]

    def clean_to(self):
        # get list of emails out of text input
        email_list = [
            x.strip() for x in self.cleaned_data['to'].split(',')
        ]

        for email in email_list:
            validate_email(email)

        return email_list

    def clean_attachment(self):
        # if attachment is empty
        if not self.cleaned_data['attachment']:
            return ''

        # otherwise get list of file ID
        file_ids = self.cleaned_data['attachment'][:-1].split(',')
        for id in file_ids:
            if not File.objects.filter(pk=id).exists():
                raise forms.ValidationError(
                    _('File with ID %d does not exist') % id
                )

        return file_ids

    def _fetch_receiver_ids(self):
        receiver_list = []

        for email in self.cleaned_data['to']:
            # look for user with same email
            user_qs = CUser.objects.filter(email=email)
            if user_qs:
                receiver_list.append(user_qs[0].id)
            else:  # otherwise create user
                user = CUser.objects.create_receiver_user(email)
                receiver_list.append(user.id)
        return receiver_list

    def save(self):
        # clean up the To data before saving
        self.cleaned_data['to'] = self._fetch_receiver_ids()
        message = super(MessageForm, self).save()

        # then add m2m relationship after saving
        message.receivers = self.cleaned_data['to']
        message.files = self.cleaned_data['attachment']

        # add signature to the main message
        message.message = re.sub(
            r'(<div id="signature">).*(</div>)',
            ur'\1{}\2'.format(self.cleaned_data['signature']),
            message.message
        )

        # add expired_at
        message.expired_at = message.created_at + timedelta(
            days=settings.MESSAGE_EXPIRED_AFTER
        )

        message.save()
        return message
