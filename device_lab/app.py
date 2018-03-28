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
from handlers.selenium_grid import SeleniumGridListHandler


def set_base_url(base_url, api_endpoints):
    return list((urljoin(base_url, path), handler)
                for path, handler in api_endpoints)


def main():
    # set api base url
    api_endpoints = set_base_url(API_BASE_URL, [
        (r"capabilities", SeleniumGridListHandler),
    ])
    # add spec endpoint
    append_spec_endpoint(api_endpoints, API_BASE_URL)
    # add swagger ui endpoint
    append_swagger_ui_endpoint(api_endpoints, STATIC_BASE_URL)

    application = tornado.web.Application(api_endpoints, **TORNADO_SETTINGS)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
