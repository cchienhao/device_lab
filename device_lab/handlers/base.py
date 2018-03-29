import json
import traceback

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, DELETE, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()

    def get_error_message(self, **kwargs):
        if 'exc_info' not in kwargs:
            return self._reason
        type_, value_, traceback_ = kwargs['exc_info']
        if isinstance(value_, tornado.web.MissingArgumentError):
            return value_.log_message

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        err_res = {
            'code': status_code,
            'data': {
                'message': self.get_error_message(**kwargs)
            }
        }
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            err_res['data']['traceback'] = traceback.format_exception(*kwargs["exc_info"])
        self.finish(json.dumps(err_res))

    def send_response(self, status_code, data):
        self.set_header('Content-Type', 'application/json')
        res = {
            'code': status_code,
            'data': data,
        }
        self.finish(json.dumps(res))
