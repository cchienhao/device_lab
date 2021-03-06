import tornado.gen


from handlers.base import BaseHandler
from services.selenium_grid import selenium_grid_service
from models.dto_schema import CapabilityLockSchema


class CapabilityListHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        """---
        tags:
            - capability
        description: Get available capabilities by conditions
        parameters:
            - in: query
              name: platform_name
              type: string
            - in: query
              name: device_name
              collectionFormat: multi
              type: array
              items:
                type: string
            - in: query
              name: platform_version
              collectionFormat: multi
              type: array
              items:
                type: string
            - in: query
              name: min_platform_version
              type: string
            - in: query
              name: max_platform_version
              type: string
            - in: query
              name: debug
              type: boolean
              description: if true, all capabilities will be return
        responses:
            200:
                description: available capabilities matched query conditions
        """
        debug = self.get_argument('debug', 'false')
        if 'true' == debug:
            devices = selenium_grid_service.get_all_capabilities()
        else:
            devices = selenium_grid_service.get_available_capabilities(
                platform_name=self.get_argument('platform_name'),
                device_names=self.get_arguments('device_name'),
                platform_versions=self.get_arguments('platform_version'),
                min_platform_version=self.get_argument('min_platform_version', None),
                max_platform_version=self.get_argument('max_platform_version', None),
            )
        self.send_response(200, devices)


class CapabilityLockListHandler(BaseHandler):
    def post(self):
        """---
        tags:
            - capability
        description: Lock Capability for exclusive usage
        parameters:
            - in: body
              required: true
              schema: CapabilityLock
        responses:
            201:
                description: success
        """
        cap_lock = CapabilityLockSchema.from_json(self.request.body)
        token = selenium_grid_service.lock_capability(cap_lock['capability_token'], cap_lock['timeout'])
        data = {
            'token': token,
        }
        self.send_response(201, data)


class CapabilityLockDetailHandler(BaseHandler):
    def delete(self, token):
        """---
        tags:
            - capability
        description: release locked capability
        parameters:
            - in: path
              name: token
              required: true
              type: string
        responses:
            200:
                description: success
        """
        selenium_grid_service.release_capability(token)
        self.send_response(200, {})
