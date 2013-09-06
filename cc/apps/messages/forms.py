from django import forms
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from cc.apps.content.models import File


class MessageForm(forms.Form):
    subject = forms.CharField(max_length=255, required=True)
    receivers = forms.CharField(max_length=255, required=True)
    cc_me = forms.CharField(widget=forms.CheckboxInput, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    files = forms.CharField(widget=forms.HiddenInput, required=True)

    # labels
    receivers.label = _('Add receivers')

    # error messages
    files.error_messages['required'] = _('You need to add some files')

    # HTML / CSS
    receivers.widget.attrs['class'] = 'span6'
    subject.widget.attrs['class'] = 'span6'
    message.widget.attrs['class'] = 'span6'

    def clean_receivers(self):
        receiver_list = self.cleaned_data.get('receivers').split(',')

        for email in receiver_list:
            validate_email(email)

        return receiver_list

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
