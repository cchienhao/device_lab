import json
from urllib.parse import urljoin

from marshmallow.class_registry import register
from apispec import APISpec
import tornado.web
from handlers.base import BaseHandler

from config import STATIC_PATH, API_BASE_URL


def append_spec_endpoint(api_endpoints, spec_path=r'swagger'):
    for path, handler in api_endpoints:
        if not path.startswith('/'):
            # NOTE: this is a workaround for swagger-ui, whose sub path should start with / or else will have problem
            path = '/' + path
        spec.add_path(urlspec=(path, handler))

    spec_json = json.dumps(spec.to_dict())
    class SpecHandler(BaseHandler):
        def get(self):
            self.set_header('Content-Type', 'application/json')
            self.finish(spec_json)
    api_endpoints.append((spec_path, SpecHandler))


def append_swagger_ui_endpoint(endpoints, base_url, path=r'(swagger-ui.*)'):
    # NOTE: static url must include one and only one group to indicate file name
    url = urljoin(base_url, path)
    endpoints.append((url, tornado.web.StaticFileHandler, dict(path=STATIC_PATH, default_filename="index.html")))


def register_schema(name, schema):
    register(name, schema)
    spec.definition(name, schema=schema)


spec = APISpec(
    title="Device lab API spec",
    version="0.0.1",
    plugins=(
        'apispec.ext.tornado',
        'apispec.ext.marshmallow',
    ),
    basePath=API_BASE_URL,
)
