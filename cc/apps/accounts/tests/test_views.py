from django.test import TestCase
from accounts.models import WhamUser
from django.core.urlresolvers import reverse
from django.test.client import Client


class AccountViewTestCases(TestCase):
    def test_index(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_login(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_register(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)

    def test_teaser(self):
        resp = self.client.get(reverse('teaser'))
        self.assertEqual(resp.status_code, 200)


class RegisterUserViewTestCases(TestCase):
    def test_register_test_user_1(self):
        resp = self.client.post(reverse('register'), {
            'username': 'test_user_1',
            'email': 'test_user_1@hotmail.com',
            'password1': 'test_user_1',
            'password2': 'test_user_1'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/')


class LoginUserViewTestCases(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = WhamUser.objects.create_user(
            'test_user_1',
            'test1@example.com',
            'test_user_1'
        )

    def test_login_user_view(self):
        #correct combination of username and password
        resp = self.client.post(reverse('login'), {
            'next': '',
            'username': 'test_user_1',
            'password': 'test_user_1'
        }, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.context['user'].username, 'test_user_1')

        #empty password and username
        resp = self.client.post(reverse('login'), {
            'next': '',
            'username': '',
            'password': ''
        })
        self.assertEqual(resp.status_code, 200)
        #self.assertEqual(resp.context['user'].username,'test_user_1')

        # Correct login, logout and go back with the browser <BACK> button.
        resp = self.client.post(reverse('login'), {
            'next': '',
            'username': 'test_user_1',
            'password': 'test_user_1'
        }, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.context['user'].username, 'test_user_1')

        resp = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'].username, '')

    def test_login_fail_view(self):
        """
        If login fails, system debug information should not be shown to users
        """
        resp = self.client.post(reverse('login'), {
            'next': '',
            'username': 'test_user_1',
            'password': 'test_user_1'
        }, follow=True)
