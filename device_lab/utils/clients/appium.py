from urllib.parse import urljoin

import tornado.gen
from tornado.httpclient import AsyncHTTPClient


class AppiumClient(object):
    def __init__(self, http=None):
        self._http = AsyncHTTPClient() if http is None else http  # type: AsyncHTTPClient

    @tornado.gen.coroutine
    def get_sessions(self, appium_url):
        """
        get all devices under specific hub
        :param hub_url:
        :return: devices' configuration and status
        """
        api_url = urljoin(appium_url, 'wd/hub/sessions')
        res = yield self._http.fetch(api_url)
        return res
