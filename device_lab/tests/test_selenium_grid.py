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

    def test_query_capabilities(self):
        caps = self.service.get_available_capabilities(platform_name='ios')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)

        caps = self.service.get_available_capabilities(platform_name='ios', platform_version=['1'])
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'}]
        self.assertEqual(expected, caps)

        caps = self.service.get_available_capabilities(platform_name='ios', min_platform_version='3')
        self.assertEqual([], caps)

        caps = self.service.get_available_capabilities(platform_name='ios', max_platform_version='0')
        self.assertEqual([], caps)

        caps = self.service.get_available_capabilities(platform_name='ios', min_platform_version='0')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)

        caps = self.service.get_available_capabilities(platform_name='ios', max_platform_version='3')
        expected = [{'capabilities': {'platformName': 'ios', 'version': '1', 'UDID': 'udid1'}, 'appium_url': 'appium_url1'},
                    {'capabilities': {'platformName': 'ios', 'version': '2', 'UDID': 'udid2'}, 'appium_url': 'appium_url2'}]
        self.assertEqual(expected, caps)


class TestSimpleLockManager(unittest.TestCase):
    def setUp(self):
        self.expired = 2
        self.lock = SimpleLockManager(expired=self.expired)

    def test_lock_acquire_and_release(self):
        self.assertFalse(self.lock.is_lock('lock1'))
        self.lock.acquire('lock1')
        self.assertTrue(self.lock.is_lock('lock1'))
        with self.assertRaises(RuntimeError) as context:
            self.lock.acquire('lock1')
        self.assertTrue('cannot lock: lock1' in str(context.exception))
        self.lock.release('lock1')
        self.assertFalse(self.lock.is_lock('lock1'))

    def test_lock_expired(self):
        self.lock.acquire('lock1')
        self.assertTrue(self.lock.is_lock('lock1'))
        sleep(self.expired - 1)
        self.lock.release_expired_keys()
        self.assertTrue(self.lock.is_lock('lock1'))
        sleep(self.expired)
        self.lock.release_expired_keys()
        self.assertFalse(self.lock.is_lock('lock1'))




# this dto must be refactored !
_GRID_RAW_DATA = {'http://10.32.52.92:4444/': {'nodes': [{'class': 'DefaultRemoteProxy',
    'id': 'http://10.32.60.38:4723',
    'protocols': {'web_driver': {'browsers': {'': {'10.1': [{'busy': False,
          'capabilities': {'UDID': 'F0F743D2-839B-4809-B404-B19AB4CDD31D',
           'browserName': '',
           'deviceName': 'iPad Air',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '0EF9048F-873E-4A51-8A50-83B1316103AF',
           'browserName': '',
           'deviceName': 'iPad Air 2',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'B31B314D-CE93-4F94-AF81-89E2F1AB45C4',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9 inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '3881EFC3-30B6-4045-BB57-94BE0035C1AD',
           'browserName': '',
           'deviceName': 'iPad Pro (9.7 inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '22CB399C-3F23-4617-A1FD-646A3028E4C2',
           'browserName': '',
           'deviceName': 'iPhone 5',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '3C5FBE8F-2EA3-4A6C-916B-D2B4C75F7BA0',
           'browserName': '',
           'deviceName': 'iPhone 5s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '28A85B2E-5F39-400B-BCF0-7E3C92539286',
           'browserName': '',
           'deviceName': 'iPhone 6',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'FA43DE1D-86B3-4CCC-8542-462D003DF0AE',
           'browserName': '',
           'deviceName': 'iPhone 6 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '62A53527-DCBC-4D86-9208-F3243A90E2D3',
           'browserName': '',
           'deviceName': 'iPhone 6s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '5E1CC136-02AB-4562-900F-31D46D74140E',
           'browserName': '',
           'deviceName': 'iPhone 6s Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'F2E77501-3B2B-4A84-9D74-D3418B1F57E0',
           'browserName': '',
           'deviceName': 'iPhone 7',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '68E4233E-46A9-4517-9F4B-03C013B14728',
           'browserName': '',
           'deviceName': 'iPhone 7 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}},
         {'busy': False,
          'capabilities': {'UDID': '6E4FD518-6C95-4EA6-A900-F147665487F3',
           'browserName': '',
           'deviceName': 'iPhone SE',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.1'}}],
        '11.1': [{'busy': False,
          'capabilities': {'UDID': '93BDAE87-5C55-4425-9F4E-42F65DDAFFD9',
           'browserName': '',
           'deviceName': 'iPad (5th generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '81D734EE-E7FE-4CA7-93F4-AC83C99D0901',
           'browserName': '',
           'deviceName': 'iPad Air',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '13867893-6A75-4118-9E78-9B12332D0D0B',
           'browserName': '',
           'deviceName': 'iPad Air 2',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'B1EDE8B9-848A-4C5C-B308-D308D6178FC0',
           'browserName': '',
           'deviceName': 'iPad Pro (10.5-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'C704E8C5-331C-4B3F-894F-72AAE931ACAB',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '77795E7A-25EF-4617-A126-4A482B87EED5',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9-inch) (2nd generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'DA68B6C3-6DFB-480B-9D44-FE5BF36465E5',
           'browserName': '',
           'deviceName': 'iPad Pro (9.7-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '9FEA4BD8-3F4B-47CA-9C6F-E8F8524B271F',
           'browserName': '',
           'deviceName': 'iPhone 5s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'DCB7DBB8-E7D6-4085-9838-974B12B8FE50',
           'browserName': '',
           'deviceName': 'iPhone 6',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '19E12E8D-D37D-4860-899B-E7C46155E907',
           'browserName': '',
           'deviceName': 'iPhone 6 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'C1CF37B8-EC69-4F7B-9B69-141A5FB11C59',
           'browserName': '',
           'deviceName': 'iPhone 6s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'D47299EA-0B69-4C49-931D-DD44D82D3DCC',
           'browserName': '',
           'deviceName': 'iPhone 6s Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '300937E3-5F0C-4380-8957-F543F82EC818',
           'browserName': '',
           'deviceName': 'iPhone 7',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'B1F28E64-1C4C-435A-971C-5E0B75FAB10D',
           'browserName': '',
           'deviceName': 'iPhone 7 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '58A0833A-5D1D-4B15-A747-6CA40DBF21EB',
           'browserName': '',
           'deviceName': 'iPhone 8',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'BA96BA7D-4660-4996-ABF0-F7325BEFF12F',
           'browserName': '',
           'deviceName': 'iPhone 8 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'E60AC3B3-DE20-409E-A149-17E64A98ADFA',
           'browserName': '',
           'deviceName': 'iPhone SE',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}},
         {'busy': False,
          'capabilities': {'UDID': '9FF4E068-1B5C-4B70-A365-E0BFBD6D0378',
           'browserName': '',
           'deviceName': 'iPhone X',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.1'}}],
        '11.2': [{'busy': False,
          'capabilities': {'UDID': '3535422E-64BD-4A13-B1AF-6031E02F4F3A',
           'browserName': '',
           'deviceName': 'iPad (5th generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '038659F5-E9BB-4813-BB17-1E9B98783D8D',
           'browserName': '',
           'deviceName': 'iPad Air',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': 'AF511084-00CC-4E53-A035-83795C55530C',
           'browserName': '',
           'deviceName': 'iPad Air 2',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '80C1BDE2-6EE9-4676-871D-D050CEEF078B',
           'browserName': '',
           'deviceName': 'iPad Pro (10.5-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': 'F5B59A42-2BFE-4E99-82AB-D2B0876C1913',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '298483D4-1838-4F17-BDBF-404ADB9A637E',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9-inch) (2nd generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '64965A7A-6847-46C7-8CFE-0958FFBE97A6',
           'browserName': '',
           'deviceName': 'iPad Pro (9.7-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '666328B1-7CCC-4E7B-B954-0EAAE3FDCEA8',
           'browserName': '',
           'deviceName': 'iPhone 5s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': 'E30AFF56-8C6F-4526-872A-9E814861543B',
           'browserName': '',
           'deviceName': 'iPhone 6',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '67F32BB5-E8A4-40BB-911F-063F25A2478A',
           'browserName': '',
           'deviceName': 'iPhone 6 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '10E8FE14-3C78-4640-83C7-E20F43E62B17',
           'browserName': '',
           'deviceName': 'iPhone 6s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '6BEBA440-C4E2-4BB3-8CAB-9FC1270B258E',
           'browserName': '',
           'deviceName': 'iPhone 6s Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': 'CC0F86BF-3EA1-4FFD-8366-4DB0A4989ADE',
           'browserName': '',
           'deviceName': 'iPhone 7',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '216DF2D3-497A-4153-8402-05AF07A02DA4',
           'browserName': '',
           'deviceName': 'iPhone 7 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '597588C5-F59F-4F5E-BD86-44F7EBCD2388',
           'browserName': '',
           'deviceName': 'iPhone 8',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '76EC0951-6BE1-4DFC-8F7A-CE0487E54513',
           'browserName': '',
           'deviceName': 'iPhone 8 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '11A526D7-4910-4EB8-828E-ADADD0709120',
           'browserName': '',
           'deviceName': 'iPhone SE',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}},
         {'busy': False,
          'capabilities': {'UDID': '55400596-C5FA-4752-A980-877C685638E7',
           'browserName': '',
           'deviceName': 'iPhone X',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2'}}],
        '11.2.6': [{'busy': False,
          'capabilities': {'UDID': '51e2a8986114c1aaa0bbe2b222114efe690c38b5',
           'browserName': '',
           'deviceName': '',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '11.2.6'}}],
        'name': '',
        'version': '11.2.6'}},
      'name': 'WebDriver'}},
    'version': '3.7.1'}]},
 'http://xia01-i01-hbt02.lab.rcch.ringcentral.com:4444/': {'nodes': [{'class': 'DefaultRemoteProxy',
    'id': 'http://10.32.60.65:4723',
    'protocols': {'web_driver': {'browsers': {'': {'10.3.1': [{'busy': False,
          'capabilities': {'UDID': '9211AA1A-5B05-4482-9149-0B6A312C6DAD',
           'browserName': '',
           'deviceName': 'appiumTest-728f6deb-94b2-49f2-bb84-ba509dfe190e',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '72D62A2C-3917-49A3-A982-650BA41B3EA3',
           'browserName': '',
           'deviceName': 'iPad (5th generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '6B9CD1E9-6AA7-4C30-90AF-412DE4D88988',
           'browserName': '',
           'deviceName': 'iPad Air',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'FF437145-C4E5-4C70-951E-2B9BB49225CB',
           'browserName': '',
           'deviceName': 'iPad Air 2',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'CCC19AB0-5E42-4CC5-AE67-9AEB2EC71963',
           'browserName': '',
           'deviceName': 'iPad Pro (10.5-inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '6BCE6A33-D6DC-4E18-800E-1F61697121F8',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9 inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '0D52CA8A-8E5B-41AD-B642-E36A052B12B3',
           'browserName': '',
           'deviceName': 'iPad Pro (12.9-inch) (2nd generation)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'B92D8B8E-BB43-4D31-BBEA-60AEF4F74DEE',
           'browserName': '',
           'deviceName': 'iPad Pro (9.7 inch)',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '44DEB228-FD69-4D06-8E7C-5F187A52CE90',
           'browserName': '',
           'deviceName': 'iPhone 5',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': 'FE04AD04-4DD7-42D5-925E-5F3856395B72',
           'browserName': '',
           'deviceName': 'iPhone 5s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '6C11C3A1-8E74-419C-85B6-A31715D98254',
           'browserName': '',
           'deviceName': 'iPhone 6',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '7264814A-044A-4551-AC6B-09734D520FDC',
           'browserName': '',
           'deviceName': 'iPhone 6 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '4613D20F-480F-4289-A848-D3F21FAAF27C',
           'browserName': '',
           'deviceName': 'iPhone 6s',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '083975C1-CEB9-4489-B512-956E7C58AAEF',
           'browserName': '',
           'deviceName': 'iPhone 6s Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '6351DFC1-A1E0-447A-BF23-3B1A50B89C90',
           'browserName': '',
           'deviceName': 'iPhone 7',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '0BC1BEAC-595E-41EE-AD34-36280375BB66',
           'browserName': '',
           'deviceName': 'iPhone 7 Plus',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}},
         {'busy': False,
          'capabilities': {'UDID': '0E72F56A-E39E-4456-BBD3-74D73645C67E',
           'browserName': '',
           'deviceName': 'iPhone SE',
           'maxInstances': 1,
           'platform': 'MAC',
           'platformName': 'ios',
           'version': '10.3.1'}}],
        'name': '',
        'version': '10.3.1'}},
      'name': 'WebDriver'}},
    'version': '3.7.1'}]}}