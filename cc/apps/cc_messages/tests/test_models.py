from django.test import TestCase

from ..models import Message
from cc.apps.accounts.models import CUser


class MessageModelTestCases(TestCase):
    fixtures = ['fixture_users.json']

    def test_create_user_default_values(self):
        msg = Message.objects.create(
            subject='Foo',
            cc_me=True,
            message='Bar',
            notify_email_opened=True,
            notify_link_clicked=False,
            owner=CUser.objects.get(pk=1),
        )
        self.assertEqual(msg.subject, 'Foo')
        self.assertIs(len(msg.receivers.all()), 0)
        self.assertIs(len(msg.files.all()), 0)
        self.assertIsNone(msg.key_page)
        self.assertIs(msg.link_text, u'')
        self.assertIsNone(msg.group)
