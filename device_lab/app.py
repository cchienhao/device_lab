from urllib.parse import urljoin

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.auth
import tornado.gen
import tornado.concurrent
import tornado.web

from config import PORT, DEBUG_MODE
from spec import append_spec_endpoint
from handlers.selenium_grid import SeleniumGridListHandler


def set_base_url(base_url, api_endpoints):
    return list((urljoin(base_url, path), handler)
                for path, handler in api_endpoints)


def main():
    base_url = r'/device_lab/api/v1/'
    api_endpoints = set_base_url(base_url, [
        (r"capabilities", SeleniumGridListHandler),
    ])
    append_spec_endpoint(api_endpoints, base_url, path='swagger')
    application = tornado.web.Application(api_endpoints, debug=DEBUG_MODE)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
