from urllib.parse import urljoin

import tornado.gen
from tornado.httpclient import AsyncHTTPClient


class SeleniumGridClient(object):
    def __init__(self, http=None):
        self._http = AsyncHTTPClient() if http is None else http  # type: AsyncHTTPClient

    @tornado.gen.coroutine
    def get_devices_by_hub_url_async(self, hub_url):
        """
        get all devices under specific hub
        :param hub_url:
        :return: devices' configuration and status
        """
        api_url = urljoin(hub_url, '/grid/admin/ShowAllNodesServlet')
        res = yield self._http.fetch(api_url)
        return res


selenium_grid_client = SeleniumGridClient()
