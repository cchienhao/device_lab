import json
from urllib.parse import urljoin

from apispec import APISpec
import tornado.web

spec = APISpec(
    title="Device lab API spec",
    version="0.0.1",
    plugins=(
        'apispec.ext.tornado',
    ),
)


def append_spec_endpoint(api_endpoints, base_url, path='swagger'):
    for urlspec in api_endpoints:
        spec.add_path(urlspec=urlspec)

    spec_json = json.dumps(spec.to_dict())
    class SpecHandler(tornado.web.RequestHandler):
        def get(self):
            self.set_header('Content-Type', 'application/json')
            self.finish(spec_json)
    url = urljoin(base_url, path)
    api_endpoints.append((url, SpecHandler))

