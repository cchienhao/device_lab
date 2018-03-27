from urllib.parse import urljoin

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.auth
import tornado.gen
import tornado.concurrent
import tornado.web

from config import PORT, DEBUG_MODE
from handlers.selenium_grid import SeleniumGridListHandler


def set_base_url(handlers):
    base_url = r'/device_lab/api/v1/'
    return list((urljoin(base_url, path), handler)
                for path, handler in handlers)


def main():
    application = tornado.web.Application(set_base_url([
        (r"capabilities", SeleniumGridListHandler),
    ]), debug=DEBUG_MODE)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
