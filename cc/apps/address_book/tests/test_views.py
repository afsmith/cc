from django.core.urlresolvers import reverse

from cc.libs.test_utils import ClientTestCase


class AddressBookViewTestCases(ClientTestCase):
    fixtures = [
        'fixture_users.json', 'fixture_payments.json'
    ]
