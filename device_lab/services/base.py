class BaseServiceException(Exception):
    # error code should conform with HTTP status code, or else need to map in handlers layer
    INVALID_CODE = 400
    NOT_FOUND_CODE = 404
    CONFLICT_CODE = 409

    def __init__(self, err_code, err_msg):
        super().__init__(err_msg)
        self.err_code = err_code
        self.err_msg = err_msg
