import json
import tornado.gen


from handlers.base import BaseHandler
from services.selenium_grid import selenium_grid_service


class SeleniumGridListHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        devices = selenium_grid_service.get_devices()
        self.write(json.dumps(devices))
