from urllib.parse import urljoin

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.auth
import tornado.gen
import tornado.concurrent
import tornado.web

from config import PORT, TORNADO_SETTINGS, API_BASE_URL, STATIC_BASE_URL
from spec import append_spec_endpoint, append_swagger_ui_endpoint

from handlers.selenium_grid import CapabilityListHandler, CapabilityLockListHandler, CapabilityLockDetailHandler


def set_base_url(api_endpoints, base_url):
    return list((urljoin(base_url, path), handler)
                for path, handler in api_endpoints)


def main():
    # NOTE: path here will be join with base_url later
    # NOTE: path here should end with /?$ for compatibility
    # NOTE: use named group so that apispec could generate proper path pattern
    api_endpoints = [
        (r"capabilities/?$", CapabilityListHandler),
        (r"capabilities-lock/?$", CapabilityLockListHandler),
        (r"capabilities-lock/(?P<token>[^/]+)/?$", CapabilityLockDetailHandler),
    ]
    # add spec endpoint
    append_spec_endpoint(api_endpoints)
    endpoints = set_base_url(api_endpoints, API_BASE_URL)

    # add swagger ui endpoint
    append_swagger_ui_endpoint(endpoints, STATIC_BASE_URL)

    application = tornado.web.Application(endpoints, **TORNADO_SETTINGS)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
