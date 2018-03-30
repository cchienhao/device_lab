import string
import secrets

default_alphabet = string.ascii_letters + string.digits


def new_random_string(size, alphabet=default_alphabet):
    return ''.join(secrets.choice(alphabet) for _ in range(20))
