from __future__ import absolute_import

from django import forms

from .models import File

"""
Definitions of various forms related to content management.
"""


class FileImportForm(forms.Form):
    """
    Form which provides interface for file uploads.
    """

    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'id': 'file',
            'class': 'file',
            'style': 'display: none;'
        })
    )

    def is_supported_file(self):
        return File.is_supported_file(self.cleaned_data['file'].name)
