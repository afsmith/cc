from django import forms
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from .models import Message
from cc.apps.content.models import File
from cc.apps.accounts.models import CUser
from cc.apps.accounts.services import create_group

import re


class MessageForm(forms.ModelForm):
    attachment = forms.IntegerField(
        label=_('Attachment'), widget=forms.HiddenInput
    )
    to = forms.CharField()
    signature = forms.CharField(required=False)

    class Meta:
        model = Message
        fields = [
            'subject',
            'cc_me',
            'notify_email_opened',
            'notify_link_clicked',
            'message',
            'key_page',
            'link_text',
        ]
        exclude = ['receivers', 'owner', 'group', 'files']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
            'key_page': forms.Select(
                choices=[('', '----------')],
                attrs={'class': 'form-control'}
            ),
            'link_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _(
                    'Add your link text (this will replace [link] '
                    'in your message ''after you send it)'
                ),
            })
        }

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        # manually order the fields
        self.fields.keyOrder = [
            'to',
            'subject',
            'cc_me',
            'notify_email_opened',
            'notify_link_clicked',
            'message',
            'link_text',
            'signature',
            'attachment',
            'key_page',
        ]
        self.fields['link_text'].required = True

    def clean_to(self):
        # get list of emails out of text input
        email_list = [
            x.strip() for x in self.cleaned_data['to'].split(',')
        ]

        for email in email_list:
            validate_email(email)

        return email_list

    def clean_attachment(self):
        file_id = self.cleaned_data['attachment']
        if not File.objects.filter(pk=file_id).exists():
            raise forms.ValidationError(
                _('File with ID %d does not exist') % file_id
            )

        return file_id

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
        message.files.add(self.cleaned_data['attachment'])

        # add the receivers group and save
        message.group = create_group(message.receivers.all())

        # add signature to the main message
        message.message = re.sub(
            r'(<div id="signature">).*(</div>)',
            ur'\1{}\2'.format(self.cleaned_data['signature']),
            message.message
        )

        message.save()
        return message
