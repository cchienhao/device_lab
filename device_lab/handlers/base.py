import json
import traceback

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        err_res = {
            'code': status_code,
            'message': self._reason,
        }
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            err_res['traceback'] = traceback.format_exception(*kwargs["exc_info"])
        self.finish(json.dumps(err_res))
