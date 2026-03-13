import hashlib
import secrets
import hmac


def simple_hmac(key, data):
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()


def create_token(key):
    session = secrets.token_urlsafe(32)
    return f"{session}:{simple_hmac(key, session)}"


def verify_token(key, token):
    elements = token.split(":")
    if len(elements) != 2:
        return False
    return simple_hmac(key, elements[0]) == elements[1]


key = "super_secret_server_key"
token = create_token(key)

assert verify_token(key, "bad_token") is False
assert verify_token(key, "bad_token:abracadabra") is False
assert verify_token(key, token) is True
