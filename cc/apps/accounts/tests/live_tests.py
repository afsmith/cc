from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class UsersLiveTest(LiveServerTestCase):
    fixtures = ['test-users-content.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_login(self):
        self.browser.get(self.live_server_url + '/accounts/login/')

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Kneto CC', h1.text)

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin@cc.kneto.com')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Hey, good to see you.', body.text)

    #def test_login_and_click_on_send(self):
    #    self.test_can_login()

        #self.browser.driver.find_element_by_xpath('#').click()

