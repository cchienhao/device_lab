import string
import secrets
from functools import wraps
from urllib.parse import urlsplit, urlunsplit

default_alphabet = string.ascii_letters + string.digits


def new_random_string(size, alphabet=default_alphabet):
    return ''.join(secrets.choice(alphabet) for _ in range(size))


def on_exception_return(value_or_callable=None):
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


def get_base_url(url):
    (scheme, netloc, path, *others) = urlsplit(url)
    return urlunsplit((scheme, netloc, '/', *others))


def is_string_in_partially(s, ss, case_insensitive=True):
    if case_insensitive:
        s = s.lower()
    for _s in ss:
        if case_insensitive:
            _s = _s.lower()
        if _s in s:  # partial match
            return True
    return False
