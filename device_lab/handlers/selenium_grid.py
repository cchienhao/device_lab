import json
import tornado.gen


from handlers.base import BaseHandler
from services.selenium_grid import selenium_grid_service


class SeleniumGridListHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        devices = selenium_grid_service.get_devices(
            platform_name=self.get_argument('platform_name', None),
            platform_version=self.get_argument('platform_version', None),
            platform_version_gt=self.get_argument('platform_version_gt', None),
            platform_version_gte=self.get_argument('platform_version_gte', None),
            platform_version_lt=self.get_argument('platform_version_lt', None),
            platform_version_lte=self.get_argument('platform_version_lte', None),
        )
        self.write(json.dumps(devices))
