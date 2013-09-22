from django.test import TestCase
from django.core.urlresolvers import reverse


class RegistrationViewTestCases(TestCase):
    def test_register_GET_success(self):
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['form'].__class__.__name__, 'UserCreationForm'
        )

    def test_register_POST_success(self):
        resp = self.client.post(reverse('registration_register'), {
            'email': 'foo@cc.kneto.com',
            'password1': 'abcd1234',
            'password2': 'abcd1234',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'country': 'VN',
            'industry': 'industry-legal'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp['Location'],
            'http://testserver%s' % reverse('registration_complete')
        )


class LoginViewTestCases(TestCase):
    fixtures = ['test-users-content.json']

    def test_login_POST_success(self):
        resp = self.client.post(reverse('auth_login'), {
            'username': 'admin@cc.kneto.com',
            'password': 'admin'
        }, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.context['user'].first_name, 'marek')

    def test_login_POST_failure(self):
        """
        If login fails, system debug information should not be shown to users
        """
        resp = self.client.post(reverse('auth_login'), {
            'username': 'test_user_1',
            'password': 'test_user_1'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['form'].errors['__all__'],
            [u'Please enter a correct email address and password.'
             ' Note that both fields may be case-sensitive.']
        )
