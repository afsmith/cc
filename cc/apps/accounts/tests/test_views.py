from django.test import TestCase
from django.core.urlresolvers import reverse

from ..models import CUser


class RegistrationViewTestCases(TestCase):
    def test_register_GET_success(self):
        resp = self.client.get(reverse('accounts_register'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['form'].__class__.__name__, 'UserCreationForm'
        )

    def test_register_POST_success(self):
        resp = self.client.post(reverse('accounts_register'), {
            'email1': 'foo@cc.kneto.com',
            'email': 'foo@cc.kneto.com',
            'password1': 'abcd1234',
            'password2': 'abcd1234',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'country': 'VN',
            'industry': 'industry-legal',
            'tos': True
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp['Location'],
            'http://testserver%s' % reverse('registration_complete')
        )

    def test_register_with_mixed_case_email(self):
        resp = self.client.post(reverse('accounts_register'), {
            'email1': 'BARBAR@cC.knEto.com',
            'email': 'BARBAR@cC.knEto.com',
            'password1': 'abcd1234',
            'password2': 'abcd1234',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'country': 'VN',
            'industry': 'industry-legal',
            'tos': True
        })
        self.assertEqual(resp.status_code, 302)

        # check if DB save lowercase value
        user_qs = CUser.objects.get(email__exact='barbar@cc.kneto.com')

        # manual set this user to active
        user_qs.is_active = True
        user_qs.save()

        # then try to use that to login with mixed case
        resp = self.client.post(reverse('auth_login'), {
            'username': 'barBAr@cc.kneTO.Com',
            'password': 'abcd1234'
        }, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.context['user'].first_name, 'Foo')


class LoginViewTestCases(TestCase):
    fixtures = ['fixture_users.json']

    def test_login_GET_success(self):
        resp = self.client.get(reverse('auth_login'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['form'].__class__.__name__, 'AuthenticationForm'
        )

    def test_login_POST_success(self):
        resp = self.client.post(reverse('auth_login'), {
            'username': 'admin@cc.kneto.com',
            'password': 'admin'
        }, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.context['user'].first_name, 'marek')

    def test_login_POST_failure(self):
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
