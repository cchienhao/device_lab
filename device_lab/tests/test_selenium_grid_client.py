import tornado.testing
from tornado.testing import AsyncTestCase

from utils.clients.selenium_grid import SeleniumGridClient


class TestSeleniumGridClient(AsyncTestCase):
    @tornado.testing.gen_test
    def test_get_devices(self):
        client = SeleniumGridClient()
        url = 'http://xia01-i01-hbt02.lab.rcch.ringcentral.com:4444'
        res = yield client.get_devices_by_hub_url_async(url)
        print(res.body)

