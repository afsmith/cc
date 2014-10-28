from django import forms
#from django.core.validators import validate_email

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        '''fields = [
                                    'work_email',
                                    'work_phone',
                                    'work_fax',
                                    'work_website',
                                    'personal_email',
                                    'home_phone',
                                    'mobile_phone',
                                    'first_name',
                                    'last_name',
                                    'title',
                                    'company',
                                ]'''
        #exclude = ['user']

        widgets = {
            'user': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
