from django.test import TestCase

from cc.apps.accounts.forms import UserCreationForm


class UserCreationFormTests(TestCase):
    """
    Test the registration forms.
    """
    fixtures = ['test-users-content.json']

    def test_registration_form_success(self):
        form = UserCreationForm(data={
            'email': 'foo@cc.kneto.com',
            'password1': 'abcd1234',
            'password2': 'abcd1234',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'country': 'VN',
            'industry': 'industry-legal'
        })
        self.assertTrue(form.is_valid())

    def test_registration_form_failure(self):
        invalid_data_dicts = [
            # missing params
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': 'secret123',
                'password2': 'secret123',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'first_name', [u'This field is required.']
            )},

            # invalid email
            {'data': {
                'email': 'foo@cc',
                'password1': 'secret123',
                'password2': 'secret123',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'email', [u'Enter a valid email address.']
            )},

            # non-unique email
            {'data': {
                'email': 'admin@cc.kneto.com',
                'password1': 'secret123',
                'password2': 'secret123',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'email', [u'User with this Email address already exists.']
            )},

            # invalid choice
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': 'secret123',
                'password2': 'secret123',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'foobar',
            }, 'error': (
                'industry', [u'Select a valid choice. foobar is not one of the'
                             ' available choices.']
            )},

            # short password
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': 'foobar1',
                'password2': 'foobar1',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'password1', [u'The password must be at least 8 characters'
                              ' long.']
            )},

            # numeric password
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': '12345678',
                'password2': '12345678',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'password1', [u'The password must contain at least one letter'
                              ' and at least one digit or punctuation'
                              ' character.']
            )},

            # alpha password
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': 'aaaaaaaa',
                'password2': 'aaaaaaaa',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'password1', [u'The password must contain at least one letter'
                              ' and at least one digit or punctuation'
                              ' character.']
            )},

            # mismatch password
            {'data': {
                'email': 'foo@cc.kneto.com',
                'password1': 'abcd1234',
                'password2': 'abcd12345',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'country': 'VN',
                'industry': 'industry-legal',
            }, 'error': (
                'password2', [u'Passwords don\'t match.']
            )},
        ]

        for invalid_dict in invalid_data_dicts:
            form = UserCreationForm(data=invalid_dict['data'])
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors[invalid_dict['error'][0]],
                invalid_dict['error'][1]
            )
