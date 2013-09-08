from django import forms
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'span6'}),
            'message': forms.Textarea(attrs={'class': 'span6'}),
            'attachment': forms.HiddenInput(),
        }

        error_messages = {
            'attachment': {
                'required': _('You need to add one file.'),
            },
        }

    def clean_receivers(self):
        receiver_list = self.cleaned_data.get('receivers').split(',')

        for email in receiver_list:
            validate_email(email)

        return receiver_list

    '''
    def clean_files(self):
        file_list = self.cleaned_data.get('files').split(',')

        for file_id in file_list:
            if not file_id.isdigit():
                raise forms.ValidationError(
                    _('File IDs must be integer')
                )
            if not File.objects.filter(pk=file_id).exists():
                raise forms.ValidationError(
                    _('File with ID %s does not exist') % file_id
                )

        return file_list
    '''
