from django.test import LiveServerTestCase

from cc.apps.tracking.models import TrackingEvent, TrackingSession

from selenium import webdriver
import time


class ViewMessageLiveTest(LiveServerTestCase):
    fixtures = ['view_message.json']

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(3)
        super(ViewMessageLiveTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(ViewMessageLiveTest, cls).tearDownClass()

    def test_view_message_tracking_time(self):
        self.browser.get(
            self.live_server_url
            + '/view/100/?token=0ObtsIKxyzNzaeawg4x4Ivlwt5Ikl'
        )

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Hieu test message', h1.text)

        # wait for 5 sec and navigate to next page
        time.sleep(5)
        self.browser.find_element_by_class_name('right').click()

        for i in range(5):
            # stay in page 2, 3, 4, 5, 6 for 1 sec
            time.sleep(1)
            self.browser.find_element_by_class_name('right').click()

        # then go to home page to close the session
        self.browser.get(self.live_server_url)

        # there should be 1 tracking session and 7 tracking events
        self.assertEqual(TrackingSession.objects.count(), 1)
        self.assertEqual(TrackingEvent.objects.count(), 7)

        # and the time in each event should be correct
        # (there can be tolerance that's less than 1 second)
        for i in range(1, 8):
            tt = TrackingEvent.objects.get(page_number=i).total_time / 10
            pv = TrackingEvent.objects.get(page_number=i).page_view
            self.assertEqual(pv, 1)
            if i == 1:
                self.assertIn(tt, [5, 6]) # 5-6 sec
            elif i == 7:
                self.assertEqual(tt, 0) # 0 sec
            else:
                self.assertIn(tt, [1, 2]) # 1-2 sec

            # print to see the actual time
            print TrackingEvent.objects.get(page_number=i).total_time / 10.0
