from django import forms

from .models import Contact

from os.path import splitext
import csv


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact

        widgets = {
            'user': forms.HiddenInput()
        }


class ImportContactForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        filename = self.cleaned_data['file'].name
        ext = splitext(filename)[1].lower()
        if ext != '.csv':
            raise forms.ValidationError('You should upload CSV file only')
        return self.cleaned_data['file']

    def save(self, user):
        result = []
        reader = csv.DictReader(self.cleaned_data['file'])
        for row in reader:
            work_email = row.get('work_email', '')
            if Contact.objects.filter(
                work_email__iexact=work_email,
                user=user
            ):
                result.append('Work email duplicated: {}'.format(work_email))
                continue
            try:
                Contact.objects.create(
                    work_email=work_email,
                    work_phone=row.get('work_phone', ''),
                    work_fax=row.get('work_fax', ''),
                    work_website=row.get('work_website', ''),
                    personal_email=row.get('personal_email', ''),
                    home_phone=row.get('home_phone', ''),
                    mobile_phone=row.get('mobile_phone', ''),
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                    title=row.get('title', ''),
                    company=row.get('company', ''),
                    user=user,
                )
            except Exception as e:
                result.append('Error occured: {}'.format(e.__str__()))

        return result or ['Done']
