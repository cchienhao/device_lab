import string
import secrets
from functools import wraps

default_alphabet = string.ascii_letters + string.digits


def new_random_string(size, alphabet=default_alphabet):
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def on_exception_return(value_or_callable):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if callable(value_or_callable):
                    return value_or_callable(e)
                return value_or_callable
        return wrapper
    return decorator
