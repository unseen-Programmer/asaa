import json
import requests
from jose import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


JWKS_URL = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"


def get_token_from_header(request):
    auth = request.headers.get("Authorization", None)

    if not auth:
        raise AuthenticationFailed("Authorization header missing")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthenticationFailed("Authorization header must start with Bearer")

    if len(parts) != 2:
        raise AuthenticationFailed("Invalid Authorization header")

    return parts[1]


def verify_auth0_token(token):
    jwks = requests.get(JWKS_URL).json()

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = None
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if not rsa_key:
        raise AuthenticationFailed("Unable to find matching RSA key")

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=settings.AUTH0_ISSUER,
        )
    except Exception as e:
        raise AuthenticationFailed(str(e))

    return payload
