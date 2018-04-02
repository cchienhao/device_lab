import json
import traceback

import tornado.web
from marshmallow.exceptions import ValidationError

from services.base import BaseServiceException


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, DELETE, GET, OPTIONS, HEAD')

    def options(self):
        self.set_status(204)
        self.finish()

    def set_error_status(self, **kwargs):
        if 'exc_info' in kwargs:
            type_, value_, traceback_ = kwargs['exc_info']
            if isinstance(value_, tornado.web.MissingArgumentError):
                self.set_status(400, value_.log_message)
            elif isinstance(value_, ValidationError):
                self.set_status(400, str(value_))
            elif isinstance(value_, BaseServiceException):
                self.set_status(value_.err_code, value_.err_msg)

    def write_error(self, _status_code, **kwargs):
        self.set_error_status(**kwargs)
        self.set_header('Content-Type', 'application/json')
        err_res = {
            'code': self._status_code,
            'data': {
                'message': self._reason
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
