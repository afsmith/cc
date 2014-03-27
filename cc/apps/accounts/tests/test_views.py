from django.test import TestCase
from django.core.urlresolvers import reverse

from ..models import CUser, Invitation
from cc.libs.test_utils import ClientTestCase

import json


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


class InvitationViewTestCases(ClientTestCase):
    def test_invite_success(self):
        c = self._get_client_user_stripe()
        resp = c.post(reverse('accounts_invite'), {
            'email': 'ndhieu88@gmail.com'
        })
        json_resp = json.loads(resp.content)
        self.assertEqual(json_resp.get('status'), 'OK')

    def test_invite_failure(self):
        c = self._get_client_user_stripe()
        # duplicate email
        resp = c.post(reverse('accounts_invite'), {
            'email': 'foo@cc.kneto.com'
        })
        json_resp = json.loads(resp.content)
        self.assertEqual(json_resp.get('status'), 'ERROR')
        self.assertEqual(
            json_resp.get('message'),
            u'* Invitation with this Email already exists.'
        )

        # invalid email
        resp = c.post(reverse('accounts_invite'), {
            'email': 'fooooooo'
        })
        json_resp = json.loads(resp.content)
        self.assertEqual(json_resp.get('status'), 'ERROR')
        self.assertEqual(
            json_resp.get('message'),
            u'* Enter a valid email address.'
        )

    def test_remove_invitation_success(self):
        c = self._get_client_user_stripe()
        resp = c.post(reverse(
            'remove_invitation', kwargs={'invitation_id': 1}
        ))
        self.assertEqual(resp.content, '{}')
        self.assertIs(Invitation.objects.count(), 0)
