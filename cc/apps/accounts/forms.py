from django import forms
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField, PasswordResetForm
)
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import CUser


class UserCreationForm(forms.ModelForm):
    '''
    Form for creating new users. Includes all the required
    fields, plus a repeated password.
    '''
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput
    )
    email1 = forms.EmailField(label=_("E-mail"))
    email = forms.EmailField(label=_("Repeat email"))
    country = forms.ChoiceField(
        widget=forms.Select, choices=settings.COUNTRY_CHOICES
    )
    industry = forms.ChoiceField(
        widget=forms.Select, choices=settings.INDUSTRY_CHOICES
    )
    tos = forms.BooleanField(
        label=_(
            'I have read and agree to the <a href="{}">Terms of Service</a>'
            .format(settings.TOS_URL)
        ),
        widget=forms.CheckboxInput(attrs={'class': 'label_checkbox'}),
        error_messages={
            'required': _('You must agree to the terms to register')
        }
    )

    PASSWORD_MIN_LENGTH = 8

    class Meta:
        model = CUser
        fields = (
            'first_name',
            'last_name',
            'email1',
            'email',
            'country',
            'industry',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        # make all fields required
        for key in self.fields:
            self.fields[key].required = True

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # At least PASSWORD_MIN_LENGTH long
        if len(password1) < self.PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(
                _('The password must be at least %d characters long.')
                % self.PASSWORD_MIN_LENGTH
            )

        # At least one letter and one non-letter
        first_isalpha = password1[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password1):
            raise forms.ValidationError(
                _('The password must contain at least one letter and '
                  'at least one digit or punctuation character.')
            )

        return password1

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords don\'t match.'))
        return password2

    def clean_email(self):
        # Check that the two email entries match
        email1 = self.cleaned_data.get('email1')
        email = self.cleaned_data.get('email')
        if email1 and email and email1 != email:
            raise forms.ValidationError(_('Email addresses don\'t match.'))
        return email

    def clean(self):
        # allow receiver to update account by bypassing unique in email field
        email = self.cleaned_data.get('email')
        if email:
            user_qs = CUser.objects.filter(email__iexact=email)
            if user_qs and user_qs[0].country != 'N/A':
                raise forms.ValidationError(
                    _('User with this email address already exists.')
                )
        return self.cleaned_data


class UserChangeForm(forms.ModelForm):
    '''
    Form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    '''
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CUser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class UserPasswordResetForm(PasswordResetForm):
    error_messages = {
        'unknown': _("That email address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this email "
                      "address cannot reset the password."),
        'receiver': _("Hey, it does not look like you're registered as a "
                      "sender. Would you like to sign up?"),
    }
    email = forms.EmailField(label=_("Email"), max_length=254)

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data['email']
        self.users_cache = CUser.objects.filter(email__iexact=email)
        if not len(self.users_cache) or len(self.users_cache) > 1:
            raise forms.ValidationError(self.error_messages['unknown'])
        user = self.users_cache[0]
        if not user.is_active:
            if user.country == 'N/A':  # receiver user
                raise forms.ValidationError(
                    self.error_messages['receiver'],
                    code='receiver'
                )
            else:
                raise forms.ValidationError(self.error_messages['unknown'])
        if user.password == UNUSABLE_PASSWORD:
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(self, *args, **kwargs):
        super(UserPasswordResetForm, self).save(*args, **kwargs)
