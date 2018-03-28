import json
from urllib.parse import urljoin

from apispec import APISpec
import tornado.web

from config import STATIC_PATH

spec = APISpec(
    title="Device lab API spec",
    version="0.0.1",
    plugins=(
        'apispec.ext.tornado',
    ),
)


def append_spec_endpoint(api_endpoints, base_url, path=r'swagger'):
    for urlspec in api_endpoints:
        spec.add_path(urlspec=urlspec)

    spec_json = json.dumps(spec.to_dict())
    class SpecHandler(tornado.web.RequestHandler):
        def get(self):
            self.set_header('Content-Type', 'application/json')
            self.finish(spec_json)
    url = urljoin(base_url, path)
    api_endpoints.append((url, SpecHandler))


def append_swagger_ui_endpoint(endpoints, base_url, path=r'(swagger-ui.*)'):
    # static url must include one and only one group to indicate file name
    url = urljoin(base_url, path)
    endpoints.append((url, tornado.web.StaticFileHandler, dict(path=STATIC_PATH, default_filename="index.html")))
