from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class UsersLiveTest(LiveServerTestCase):
    fixtures = ['fixture_users.json', 'fixture_payments.json']

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(3)
        super(UsersLiveTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(UsersLiveTest, cls).tearDownClass()

    def test_login_admin(self):
        self.browser.get(self.live_server_url + '/accounts/login/')

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Kneto CC', h1.text)

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin@cc.kneto.com')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Priority call list', body.text)

    def test_login_user(self):
        self.browser.get(self.live_server_url + '/accounts/login/')

        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Kneto CC', h1.text)

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('john@cc.kneto.com')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Early Access', body.text)
