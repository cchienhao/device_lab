import tornado.gen


from handlers.base import BaseHandler
from services.selenium_grid import selenium_grid_service


class SeleniumGridListHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        """Get available capabilities endpoint
        ---
        tags:
            - capability
        summary: Get available capabilities by conditions
        parameters:
            - in: query
              name: platform_name
              required: true
            - in: query
              name: platform_version
              required: false
            - in: query
              name: min_platform_version
              required: false
            - in: query
              name: max_platform_version
              required: false
        responses:
            200:
                description: available capabilities matched query conditions
        """
        devices = selenium_grid_service.get_available_capabilities(
            platform_name=self.get_argument('platform_name'),
            platform_version=self.get_arguments('platform_version'),
            min_platform_version=self.get_argument('min_platform_version', None),
            max_platform_version=self.get_argument('max_platform_version', None),
        )
        self.send_response(200, devices)
