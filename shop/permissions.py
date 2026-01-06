from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import requests
from jose import jwt


class IsAuthenticatedWithAuth0(BasePermission):
    """
    Auth0 JWT authentication using python-jose
    - Verifies token using Auth0 JWKS
    - Validates audience & issuer
    - Sets request.auth0_user_id from `sub`
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth_header.split(" ")[1]

        try:
            # 🔐 Fetch Auth0 JWKS
            jwks = requests.get(
                f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json",
                timeout=5
            ).json()

            # ✅ Decode & verify token
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )

            auth0_user_id = payload.get("sub")

            if not auth0_user_id:
                raise AuthenticationFailed("auth0_user_id missing in token")

            # 🔥 Attach to request (used by views)
            request.auth0_user_id = auth0_user_id

            return True

        except Exception as e:
            print("AUTH0 AUTH ERROR:", e)
            raise AuthenticationFailed("Invalid or expired token")
