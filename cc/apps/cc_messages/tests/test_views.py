from django.core.urlresolvers import reverse

from cc.libs.test_utils import ClientTestCase


class MessageViewTestCases(ClientTestCase):
    fixtures = [
        'fixture_users.json', 'fixture_payments.json', 'fixture_files.json',
        'fixture_messages.json'
    ]

    def test_send_message_GET_success(self):
        c = self._get_client_user_stripe()
        resp = c.get(reverse('send'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['message_form'].__class__.__name__, 'MessageForm'
        )
        self.assertEqual(
            resp.context['message_form'].initial['message'],
            u'<br><br><br><br>[link]<br><br><div id="signature">Foobar</div>'
        )
        self.assertEqual(
            resp.context['message_form'].initial['signature'],
            u'Foobar'
        )
        self.assertEqual(
            resp.context['import_file_form'].__class__.__name__,
            'FileImportForm'
        )

    def test_send_message_POST_success(self):
        c = self._get_client_user_stripe()
        resp = c.post(reverse('send'), {
            'subject': 'Test',
            'cc_me': False,
            'notify_email_opened': False,
            'notify_link_clicked': False,
            'message': 'lala',
            'attachment': 1,
            'to': 'foo@cc.kneto.com',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['thankyou_page'])
        self.assertIn('your message is being processed', resp.content)

    def test_resend_message_success(self):
        c = self._get_client_user_stripe()
        resp = c.post(reverse('resend'), {
            'message_id': 1
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '{}')


class ViewMessageTestCases(ClientTestCase):
    fixtures = ['fixture_view_message.json']

    def test_receiver_view_message_success(self):
        resp = self.client.get(
            '{}?token=0ObtsIKxyzNzaeawg4x4Ivlwt5Ikl'.format(reverse(
                'view_message', kwargs={'message_id': 100}
            ))
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['message'].__str__(), 'Hieu test message'
        )
        self.assertEqual(
            resp.context['file'].__str__(), 'ZenCodingCheatSheet.pdf'
        )
        self.assertEqual(
            resp.context['token'].__str__(), '0ObtsIKxyzNzaeawg4x4Ivlwt5Ikl'
        )
        self.assertEqual(
            resp.context['ocl_user'].__str__(), 'foo@barrrrr.com'
        )
        self.assertFalse(resp.context['is_owner_viewing'])
        self.assertEqual(resp.context['tracking_log'].__str__(), 'CLICK_LINK')

    def test_owner_view_message_success(self):
        resp = self.client.get(
            '{}?token=l1R6PfMMBPPNn1SC7G5pGZMI2vkVpF'.format(reverse(
                'view_message', kwargs={'message_id': 100}
            ))
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['ocl_user'].__str__(), 'bar@foooooo.com')
        self.assertTrue(resp.context['is_owner_viewing'])
        self.assertIsNone(resp.context['tracking_log'])

    def test_view_message_wrong_token(self):
        self.login_required_redirect(reverse(
            'view_message', kwargs={'message_id': 100}
        ))

    def test_view_message_token_expired(self):
        resp = self.client.get(
            '{}?token=Yz6t9o71cpjnBTzvJ3Ls6eDe3zbtNp'.format(reverse(
                'view_message', kwargs={'message_id': 100}
            ))
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['ocl_expired'])
