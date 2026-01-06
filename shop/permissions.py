from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import requests
from jose import jwt, jwk

# 🔐 Cache JWKS to avoid repeated network calls (Render-safe)
_JWKS_CACHE = None


class IsAuthenticatedWithAuth0(BasePermission):
    """
    Auth0 JWT authentication using python-jose.
    - Verifies token signature using Auth0 JWKS
    - Validates audience & issuer
    - Attaches request.auth0_user_id from token `sub`
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth_header.split(" ")[1]

        try:
            # 1️⃣ Read token header (no verification yet)
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise AuthenticationFailed("Invalid token header")

            # 2️⃣ Fetch & cache JWKS
            global _JWKS_CACHE
            if _JWKS_CACHE is None:
                _JWKS_CACHE = requests.get(
                    f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json",
                    timeout=5
                ).json()

            # 3️⃣ Find matching public key
            public_key = None
            for key in _JWKS_CACHE.get("keys", []):
                if key.get("kid") == kid:
                    public_key = jwk.construct(key)
                    break

            if public_key is None:
                raise AuthenticationFailed("Public key not found")

            # 4️⃣ Verify & decode token
            payload = jwt.decode(
                token,
                public_key.to_pem().decode("utf-8"),
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )

            # 5️⃣ Attach stable Auth0 user id
            auth0_user_id = payload.get("sub")
            if not auth0_user_id:
                raise AuthenticationFailed("auth0_user_id missing in token")

            request.auth0_user_id = auth0_user_id
            return True

        except Exception as e:
            print("AUTH0 AUTH ERROR:", e)
            raise AuthenticationFailed("Invalid or expired token")
    