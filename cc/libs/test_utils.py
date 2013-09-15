from abc import ABCMeta
from django.test import client, TestCase, TransactionTestCase
import json


class LoginHelper:
    __metaclass__ = ABCMeta

    fixtures = ('test-users.json',)

    def _get_client_user(self, username='john@cc.kneto.com', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(email=username, password=password))
        return c

    def _get_client_admin(self, username='admin@cc.kneto.com', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(email=username, password=password))
        return c


class ClientTestCase(TestCase, LoginHelper):
    __metaclass__ = ABCMeta

    def should_not_accept_get(self, url):
        c = self._get_client_user()
        response = c.get(url)
        self.assertEquals(response.status_code, 405)

    def should_not_accept_post(self, url):
        c = self._get_client_user()
        response = c.post(url)
        self.assertEquals(response.status_code, 405)

    def _post_json(self, url, data=None, client=None):
        if data is None:
            data = {}

        if client is None:
            client = self._get_client()

        response = client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        return response


class TransactionalClientTestCase(TransactionTestCase, LoginHelper):
    __metaclass__ = ABCMeta
