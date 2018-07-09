from django.conf import settings
from hashlib import sha256


def hash_string(string2hash: str):

    salt = settings.SECRET_KEY.encode()
    hash_object = sha256(salt + string2hash.encode())

    return hash_object.hexdigest()
