from django.test import TestCase
from django.db import IntegrityError

from ..models import CUser, OneClickLinkToken, BillingAddress, Invitation


class CUserModelTestCases(TestCase):
    fixtures = ['fixture_users.json', 'fixture_payments.json']

    def _create_user(self):
        return CUser.objects.create_user(
            email='foo@cc.kneto.com',
            password='blah',
            first_name='Foo',
            last_name='Bar',
            country='VN',
            industry='IT',
        )

    def test_create_user_default_values(self):
        user = self._create_user()
        self.assertEqual(user.email, 'foo@cc.kneto.com')
        self.assertEqual(user.username, '')
        # user type = sender
        self.assertEqual(user.user_type, 1)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.signature, '')

    def test_create_user_with_invitation_success(self):
        # check if status of invitation is SENT
        self.assertEqual(
            Invitation.objects.get(pk=1).status, Invitation.STATUS_SENT
        )
        user = CUser.objects.create_user(
            email='foo@cc.kneto.com',
            password='blah',
            first_name='Foo',
            last_name='Bar',
            country='VN',
            industry='IT',
            invitation_code='O8oKAwG8CnDS9iRQBeFqP950PRMgiM',
        )
        self.assertEqual(user.email, 'foo@cc.kneto.com')
        # user type = sender
        self.assertEqual(user.user_type, 3)
        # invitation should change to ACCEPTED
        self.assertEqual(
            Invitation.objects.get(pk=1).status, Invitation.STATUS_ACCEPTED
        )
        # and to_user field is filled
        self.assertEqual(Invitation.objects.get(pk=1).to_user, user)

    def test_create_user_with_form_data_success(self):
        user = CUser.objects.create_user(
            email='foo@cc.kneto.com',
            email1='foo@cc.kneto.com',
            password1='blah',  # password1 and password2 are sent from form
            password2='blah',
            first_name='Foo',
            last_name='Bar',
            country='VN',
            industry='IT',
            tos=True,
            some_data='foo',
            some_other_data='bar',
        )
        self.assertEqual(user.email, 'foo@cc.kneto.com')
        self.assertEqual(user.user_type, 1)

    def test_create_user_missing_email_failure(self):
        # missing email
        with self.assertRaises(ValueError) as cm:
            CUser.objects.create_user(
                password='blah',
                first_name='Foo',
                last_name='Bar',
                country='VN',
                industry='IT',
            )
        self.assertEqual('Users must have an email address', str(cm.exception))

    def test_create_user_with_invitation_failure(self):
        # wrong invitation code
        with self.assertRaises(ValueError) as cm:
            CUser.objects.create_user(
                email='foo@cc.kneto.com',
                password='blah',
                first_name='Foo',
                last_name='Bar',
                country='VN',
                industry='IT',
                invitation_code='lalala',
            )
        self.assertEqual('Invitation code is invalid', str(cm.exception))

    def test_create_receiver_user_default_values(self):
        user = CUser.objects.create_receiver_user('foo@cc.kneto.com')
        self.assertEqual(user.email, 'foo@cc.kneto.com')
        self.assertEqual(user.first_name, 'N/A')
        self.assertEqual(user.last_name, 'N/A')
        self.assertEqual(user.country, 'N/A')
        self.assertEqual(user.industry, 'N/A')
        # user type = receiver
        self.assertEqual(user.user_type, 2)
        self.assertFalse(user.is_active)

    def test_model_properties(self):
        user = self._create_user()
        self.assertTrue(user.is_sender)

        user.user_type = 2
        self.assertTrue(user.is_receiver)

        user.user_type = 3
        self.assertTrue(user.is_invited_user)
        self.assertFalse(user.is_invited_user_has_active_subscription)

    def test_get_unused_invitations(self):
        user = self._create_user()
        self.assertFalse(user.get_unused_invitations())

        user = CUser.objects.get(pk=1)
        self.assertIs(user.get_unused_invitations(), 3)

    def test_get_active_invitations(self):
        user = self._create_user()
        self.assertFalse(user.get_active_invitations())

        user = CUser.objects.get(pk=1)
        self.assertEqual(
            user.get_active_invitations()[0],
            Invitation.objects.get(pk=1)
        )


class OneClickLinkTokenModelTestCases(TestCase):
    fixtures = ['fixture_users.json', 'fixture_payments.json']

    def test_create_OCL_default_values(self):
        user = CUser.objects.get(pk=1)
        ocl = OneClickLinkToken.objects.create(user=user)
        self.assertEqual(ocl.user, user)
        self.assertIsInstance(ocl.token, str)
        self.assertEqual(len(ocl.token), 30)
        self.assertFalse(ocl.expired)
        self.assertIsNone(ocl.expires_on)
        self.assertFalse(ocl.allow_login)


class BillingAddressTestCases(TestCase):
    fixtures = ['fixture_users.json', 'fixture_payments.json']

    def test_create_billing_address_default_values(self):
        user = CUser.objects.get(pk=1)
        ba = BillingAddress.objects.create(user=user)
        self.assertEqual(ba.user, user)
        self.assertIsNone(ba.name)
        self.assertIsNone(ba.address_line1)
        self.assertIsNone(ba.address_line2)
        self.assertIsNone(ba.address_zip)
        self.assertIsNone(ba.address_city)
        self.assertIsNone(ba.address_state)
        self.assertIsNone(ba.address_country)


class InvitationTestCases(TestCase):
    fixtures = ['fixture_users.json', 'fixture_payments.json']

    def test_create_invitation_default_values(self):
        user = CUser.objects.get(pk=1)
        invitation = Invitation.objects.create(
            from_user=user,
            to_email='foo@kneto.com',
        )
        self.assertEqual(invitation.from_user, user)
        self.assertEqual(invitation.to_email, 'foo@kneto.com')
        self.assertIsNone(invitation.to_user)
        self.assertIsInstance(invitation.code, str)
        self.assertEqual(len(invitation.code), 30)
        self.assertEqual(invitation.status, Invitation.STATUS_SENT)

    def test_create_invitation_unique_email_failure(self):
        user = CUser.objects.get(pk=1)
        with self.assertRaises(IntegrityError):
            Invitation.objects.create(
                from_user=user,
                to_email='foo@cc.kneto.com',
            )
