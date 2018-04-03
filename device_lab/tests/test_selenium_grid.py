import unittest
import tornado.testing

from utils.clients.selenium_grid import SeleniumGridClient
from services.selenium_grid import SeleniumGridService
from services.selenium_grid import SimpleLockManager
from time import sleep


class TestSeleniumGridClient(tornado.testing.AsyncTestCase):
    @tornado.testing.gen_test
    def test_get_devices(self):
        client = SeleniumGridClient()
        url = 'http://xia01-i01-hbt02.lab.rcch.ringcentral.com:4444'
        res = yield client.get_devices_by_hub_url_async(url)
        print(res.body)


class TestSeleniumGridService(unittest.TestCase):
    def setUp(self):
        self.service = SeleniumGridService()
        self.service.set_capabilities([
            {
                "capabilities": {
                    "platformName": "ios",
                    "version": "1",
                    "UDID": "udid1",
                },
                "appium_url": "appium_url1",
            },
            {
                "capabilities": {
                    "platformName": "ios",
                    "version": "2",
                    "UDID": "udid2",
                },
                "appium_url": "appium_url1",
            },
            {
                "capabilities": {
                    "platformName": "ios",
                    "version": "1",
                    "UDID": "udid1",
                },
                "appium_url": "appium_url2",
            },
            {
                "capabilities": {
                    "platformName": "ios",
                    "version": "2",
                    "UDID": "udid2",
                },
                "appium_url": "appium_url2",
            },
        ])

    def test_query_capabilities1(self):
        caps = self.service.get_available_capabilities(platform_name='ios')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)

    def test_query_capabilities2(self):
        caps = self.service.get_available_capabilities(platform_name='ios', platform_versions=['1'])
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'}]
        self.assertEqual(expected, caps)

    def test_query_capabilities3(self):
        caps = self.service.get_available_capabilities(platform_name='ios', min_platform_version='3')
        self.assertEqual([], caps)

    def test_query_capabilities4(self):
        caps = self.service.get_available_capabilities(platform_name='ios', max_platform_version='0')
        self.assertEqual([], caps)

    def test_query_capabilities5(self):
        caps = self.service.get_available_capabilities(platform_name='ios', min_platform_version='0')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)

    def test_query_capabilities6(self):
        caps = self.service.get_available_capabilities(platform_name='ios', max_platform_version='3')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)


class TestSimpleLockManager(unittest.TestCase):
    def setUp(self):
        self.expired = 2
        self.lock = SimpleLockManager()

    def test_lock_acquire_and_release(self):
        self.assertFalse(self.lock.is_lock('lock1'))
        self.lock.acquire('lock1', expired=self.expired)
        self.assertTrue(self.lock.is_lock('lock1'))
        with self.assertRaises(RuntimeError) as context:
            self.lock.acquire('lock1', expired=self.expired)
        self.assertTrue('cannot lock: lock1' in str(context.exception))
        self.lock.release('lock1')
        self.assertFalse(self.lock.is_lock('lock1'))

    def test_lock_expired(self):
        self.lock.acquire('lock1', expired=self.expired)
        self.assertTrue(self.lock.is_lock('lock1'))
        sleep(self.expired - 1)
        self.lock.release_expired_keys()
        self.assertTrue(self.lock.is_lock('lock1'))
        sleep(self.expired)
        self.lock.release_expired_keys()
        self.assertFalse(self.lock.is_lock('lock1'))

