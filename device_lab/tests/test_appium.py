import tornado.testing

from utils.clients.appium import AppiumClient


class TestSeleniumGridClient(tornado.testing.AsyncTestCase):
    @tornado.testing.gen_test
    def test_get_devices(self):
        client = AppiumClient()
        url = 'http://127.0.0.1:4723'
        res = yield client.get_sessions(url)
        print(res.body)
