import json
import tornado.gen


from handlers.base import BaseHandler
from services.selenium_grid import selenium_grid_service


class SeleniumGridListHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        devices = selenium_grid_service.get_available_capabilities(
            platform_name=self.get_argument('platform_name', None),
            platform_version=self.get_arguments('platform_version'),
            min_platform_version=self.get_argument('min_platform_version', None),
            max_platform_version=self.get_argument('max_platform_version', None),
        )
        self.write(json.dumps(devices))
