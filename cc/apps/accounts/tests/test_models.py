from django.test import TestCase

from ..models import CUser


class CUserModelTestCases(TestCase):
    def _create_user(self):
        return CUser.objects.create_user(
            email='foo@cc.kneto.com',
            password='blah',
            first_name='Foo',
            last_name='Bar',
            country='VN',
            industry='IT',
        )

    def test_create_user_success(self):
        user = self._create_user()
        self.assertEqual(user.email, 'foo@cc.kneto.com')

    def test_create_user_default_values(self):
        user = self._create_user()
        self.assertEqual(user.username, '')
        self.assertEqual(user.user_type, 1)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.signature, '')

    def test_create_receiver_user_success(self):
        user = CUser.objects.create_receiver_user('foo@cc.kneto.com')
        self.assertEqual(user.email, 'foo@cc.kneto.com')

    def test_create_receiver_user_default_values(self):
        user = CUser.objects.create_receiver_user('foo@cc.kneto.com')
        self.assertEqual(user.first_name, 'N/A')
        self.assertEqual(user.last_name, 'N/A')
        self.assertEqual(user.country, 'N/A')
        self.assertEqual(user.industry, 'N/A')
        self.assertEqual(user.user_type, 2)
        self.assertFalse(user.is_active)
