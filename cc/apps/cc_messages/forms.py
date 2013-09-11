from django import forms
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from .models import Message
from cc.apps.content.models import File
from cc.apps.accounts.models import CUser


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ('receivers',)

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'span6'}),
            'message': forms.Textarea(attrs={'class': 'span6'}),
            'attachment': forms.HiddenInput(),
        }

        # error_messages is not supported until 1.6
        '''
        error_messages = {
            'attachment': {
                'required': _('You need to add one file.'),
            },
        }
        '''

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        # add To field as a text input, 1 is the order of the field
        self.fields.insert(1, 'to', forms.CharField())

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
        print receiver_list
        return receiver_list

    def save(self, commit=True):
        # clean up the To data before saving
        self.cleaned_data['to'] = self._fetch_receiver_ids()
        message = super(MessageForm, self).save()
        # then add m2m relationship after saving
        message.receivers = self.cleaned_data['to']
        return message