# shop/authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import requests
from django.contrib.auth.models import User
from django.conf import settings
from functools import lru_cache


@lru_cache()
def get_jwks():
    """Cache JWKS to avoid fetching on every request"""
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url, timeout=5)
    response.raise_for_status()
    return response.json()


class Auth0JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header:
            return None  # DRF will handle missing auth

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed(
                "Invalid Authorization header format. Use 'Bearer <token>'"
            )

        token = parts[1]

        try:
            jwks = get_jwks()

            unverified_header = jwt.get_unverified_header(token)

            rsa_key = next(
                (
                    {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }
                    for key in jwks["keys"]
                    if key["kid"] == unverified_header["kid"]
                ),
                None,
            )

            if not rsa_key:
                raise AuthenticationFailed("No matching JWKS key found")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",  # MUST end with /
            )

            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationFailed("Token missing 'sub' claim")

            user, _ = User.objects.get_or_create(
                username=user_id,
                defaults={"email": payload.get("email", "")},
            )

            return (user, token)

        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except JWTClaimsError as e:
            raise AuthenticationFailed(f"Invalid claims: {str(e)}")
        except JWTError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception:
            raise AuthenticationFailed("Unable to validate token")

    def authenticate_header(self, request):
        return "Bearer"
