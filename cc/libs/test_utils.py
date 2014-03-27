from django.test import client, TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from abc import ABCMeta

User = get_user_model()


class LoginHelper:
    __metaclass__ = ABCMeta

    fixtures = ['fixture_users.json', 'fixture_payments.json']

    def _get_client_user(self):
        c = client.Client()
        self.assertTrue(c.login(email='john@cc.kneto.com', password='admin'))
        return c

    def _get_client_admin(self):
        c = client.Client()
        self.assertTrue(c.login(email='admin@cc.kneto.com', password='admin'))
        return c

    def _get_client_user_stripe(self):
        c = client.Client()
        self.assertTrue(c.login(email='admin@cc.kneto.com', password='admin'))
        u = User.objects.get(pk=c.session['_auth_user_id'])
        self.assertTrue(u.customer.has_active_subscription())
        return c


class ClientTestCase(TestCase, LoginHelper):
    __metaclass__ = ABCMeta

    def should_not_allow_GET_login(self, url):
        c = self._get_client_user()
        response = c.get(url)
        self.assertEqual(response.status_code, 405)

    def should_not_allow_GET(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

    def login_required_redirect(self, url):
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.redirect_chain[0][1], 302)
        self.assertIn(reverse('auth_login'), resp.redirect_chain[0][0])
