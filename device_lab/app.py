import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.auth
import tornado.gen
import tornado.concurrent

from config import PORT, DEBUG_MODE
from handlers.selenium_grid import SeleniumGridListHandler


def main():
    application = tornado.web.Application([
        (r"/", SeleniumGridListHandler),
    ], debug=DEBUG_MODE)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
