from django.test.testcases import TestCase
from django.core.urlresolvers import reverse

from .models import TrackingEvent
from cc.libs.utils import progress_formatter
from cc.libs.test_utils import ClientTestCase

import json


class CreateEventTest(ClientTestCase):
    fixtures = ['fixture_users.json']
    url = reverse('create_event')

    def test_should_add_new_event(self):
        c = self._get_client_user()
        resp = c.post(self.url, {})
        self.assertEqual(resp.status_code, 200)

    def test_should_not_allow_GET(self):
        self.should_not_allow_GET_login(self.url)


class ProgressFormatterTest(TestCase):
    
    def test_returns_zero_if_no_progress(self):
        result = progress_formatter(0)
        self.assertEqual(result, 0)
        
    def test_returns_10_if_lt15(self):
        result = progress_formatter(0.01)
        self.assertEqual(result, 10)
        result = progress_formatter(0.149)
        self.assertEqual(result, 10)
        result = progress_formatter(0.15)
        self.assertEqual(result, 20)
        
    def test_returns_round_if_lt95(self):        
        result = progress_formatter(0.249)
        self.assertEqual(result, 20)
        result = progress_formatter(0.25)
        self.assertEqual(result, 30)
        result = progress_formatter(0.849)
        self.assertEqual(result, 80)
        result = progress_formatter(0.85)
        self.assertEqual(result, 90)
        result = progress_formatter(0.949)
        self.assertEqual(result, 90)
        result = progress_formatter(0.95)
        self.assertEqual(result, 90)
        
    def test_returns_90_if_lt100(self):
        result = progress_formatter(0.951)
        self.assertEqual(result, 90)
        result = progress_formatter(0.99999)
        self.assertEqual(result, 90)
        
    def test_returns_1_if_completed(self):
        result = progress_formatter(1)
        self.assertEqual(result, 100)
