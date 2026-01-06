from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import requests
import jwt
from jwt.algorithms import RSAAlgorithm


class IsAuthenticatedWithAuth0(BasePermission):
    """
    Custom permission to authenticate requests using Auth0 JWT access tokens.
    It verifies:
    - Authorization header exists
    - Token signature using Auth0 JWKS
    - Audience and Issuer
    - Sets request.auth0_user_id from token `sub`
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth_header.split(" ")[1]

        try:
            # 🔐 Fetch Auth0 public keys (JWKS)
            jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
            jwks = requests.get(jwks_url, timeout=5).json()

            # 🔍 Read token header
            unverified_header = jwt.get_unverified_header(token)

            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == unverified_header.get("kid"):
                    rsa_key = RSAAlgorithm.from_jwk(key)
                    break

            if rsa_key is None:
                raise AuthenticationFailed("Unable to find appropriate key")

            # ✅ Decode & verify token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )

            # 🔑 SINGLE SOURCE OF USER ID
            auth0_user_id = payload.get("sub")

            if not auth0_user_id:
                raise AuthenticationFailed("auth0_user_id missing in token")

            # 🔥 Attach to request (used everywhere else)
            request.auth0_user_id = auth0_user_id

            return True

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")

        except jwt.JWTClaimsError as e:
            raise AuthenticationFailed(f"Invalid claims: {str(e)}")

        except Exception as e:
            print("AUTH0 AUTH ERROR:", e)
            raise AuthenticationFailed("Invalid authentication token")
