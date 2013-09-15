from django.test import TestCase
from django.test.client import Client

from cc.apps.accounts.models import CUser
from cc.apps.accounts.forms import UserCreationForm


class UserCreationFormTests(TestCase):
    """
    Test the registration forms.
    """
    fixtures = ['test-user.json']

    def test_registration_form(self):
        """
        Test that ``UserCreationForm`` enforces username constraints
        and matching passwords.
        """

        invalid_data_dicts = [
            # username cannot contain "/".
            {'data': {'username': 'foo/bar',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'foo'},
            'error': ('username', [u"Enter a valid username."])},
            # Already-existing username.
            {'data': {'username': 'alice',
                      'email': 'alice@example.com',
                      'password1': 'secret',
                      'password2': 'secret'},
            'error': ('username', [u"User with this Username already exists."])},
            # too short passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'foo'},
            'error': ('password1', [u"The password must be at least 8 characters long."])},

            # numeric passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': '123456789',
                      'password2': '123456789'},
            'error': ('password1', [u"The password must contain at least one letter and at least one digit or punctuation character."])},

            # alpha passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': 'abcdefghj',
                      'password2': 'abcdefghj'},
            'error': ('password1', [u"The password must contain at least one letter and at least one digit or punctuation character."])},

            # Mismatched passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': 'foofoo123',
                      'password2': 'foobar123'},
            'error': ('password2', [u"Passwords don\'t match."])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = UserCreationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(
                form.errors[invalid_dict['error'][0]],
                invalid_dict['error'][1]
            )

        form = UserCreationForm(data={
            'username': 'foo',
            'email': 'foo@example.com',
            'password1': 'validPasswd1',
            'password2': 'validPasswd1'
        })
        self.failUnless(form.is_valid())


class LoginFormTests(TestCase):
    fixtures = ['test-user.json']

    def test_login_form(self):
        invalid_data_dicts = [
            # username in wrong syntax
            {'data': {'username': 'foo/bar',
                      'password': 'foo'},
            'error': ('username', [u"Enter a valid username."])},

            {'data': {'username': 'foo,,,bar',
                      'password': 'foo'},
            'error': ('username', [u"Enter a valid username."])},

            # non-exsiting username with existing passwd
            {'data': {'username': 'foojhgjghbar',
                      'password': 'validPasswd3'},
            'error': ('username', [u"Enter a valid username."])},
            # correct username wrong passwd
            {'data': {'username': 'alice',
                      'password': ''},
            'error': ('username', [u"Enter a valid username."])},
            # correct username empty passwd
            {'data': {'username': 'alice',
                      'password': 'validPa'},
            'error': ('username', [u"Enter a valid username."])},

            # empty username and passwd
            {'data': {'username': '',
                      'password': ''},
            'error': ('username', [u"Enter a valid username."])},
            # correct passwd and empty username
            {'data': {'username': '',
                      'password': 'validPasswd3'},
            'error': ('username', [u"Enter a valid username."])},
        ]

        for invalid_dict in invalid_data_dicts:
            loggedIn = self.client.login(
                email=invalid_dict['data']['username'],
                password=invalid_dict['data']['password']
            )

            self.failIf(loggedIn)
