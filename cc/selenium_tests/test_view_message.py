from django.test import LiveServerTestCase

from cc.apps.tracking.models import TrackingEvent, TrackingSession

from selenium import webdriver
import time

'''
Live test suite for viewing message and verify the tracking data is correct.

Since Safari webdriver is only available on Selenium standalone server.
You need to download it here:
    http://selenium.googlecode.com/files/selenium-server-standalone-2.37.0.jar
And set env variable SELENIUM_SERVER_JAR before the test
    export SELENIUM_SERVER_JAR=/path/to/selenium-server-standalone-2.37.0.jar
To run this test suite alone:
    python manage.py test cc/apps/cc_messages/tests/live_tests.py
'''

def _test_view_message_tracking_time(self, go_to_url):
    self.browser.get(
        self.live_server_url
        + '/view/100/?token=0ObtsIKxyzNzaeawg4x4Ivlwt5Ikl'
    )

    #h1 = self.browser.find_element_by_tag_name('h1')
    #self.assertIn('Hieu test message', h1.text)

    # wait for 5 sec and navigate to next page
    time.sleep(5)
    self.browser.find_element_by_class_name('flexpaper_bttnPrevNext').click()

    for i in range(5):
        # stay in page 2, 3, 4, 5, 6 for 1 sec
        time.sleep(1)
        self.browser.find_element_by_class_name(
            'flexpaper_bttnPrevNext'
        ).click()

    # then go to Google to close the session
    self.browser.get(go_to_url)

    # there should be 1 tracking session and 7 tracking events
    self.assertEqual(TrackingSession.objects.count(), 1)
    self.assertEqual(TrackingEvent.objects.count(), 7)

    # and the time in each event should be correct
    # (there can be tolerance that's less than 1 second)
    for i in range(1, 8):
        tt = TrackingEvent.objects.get(page_number=i).total_time / 10
        pv = TrackingEvent.objects.get(page_number=i).page_view
        if i == 1:
            self.assertIn(tt, [3, 4, 5])  # 3-5 sec
            self.assertEqual(pv, 1)
        elif i == 7:
            self.assertEqual(tt, 0)  # 0 sec
            self.assertIn(pv, [0, 1])  # there is racing condition here
        else:
            self.assertIn(tt, [0, 1, 2])  # 0-2 sec
            self.assertEqual(pv, 1)

        # print to see the actual time
        print TrackingEvent.objects.get(page_number=i).total_time / 10.0


class ViewMessageLiveTestOnFirefox(LiveServerTestCase):
    fixtures = ['fixture_view_message.json']

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(3)
        super(ViewMessageLiveTestOnFirefox, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(ViewMessageLiveTestOnFirefox, cls).tearDownClass()

    def test_view_message_then_homepage_tracking_time(self):
        _test_view_message_tracking_time(self, self.live_server_url)

    def test_view_message_then_external_url_tracking_time(self):
        _test_view_message_tracking_time(self, 'http://google.com')


class ViewMessageLiveTestOnSafari(LiveServerTestCase):
    fixtures = ['fixture_view_message.json']

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Safari()
        cls.browser.implicitly_wait(3)
        super(ViewMessageLiveTestOnSafari, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(ViewMessageLiveTestOnSafari, cls).tearDownClass()

    def test_view_message_then_homepage_tracking_time(self):
        _test_view_message_tracking_time(self, self.live_server_url)

    def test_view_message_then_external_url_tracking_time(self):
        _test_view_message_tracking_time(self, 'http://google.com')
