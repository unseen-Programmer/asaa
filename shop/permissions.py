from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode


class IsAuthenticatedWithAuth0(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth_header.split(" ")[1]

        try:
            # 1️⃣ Get unverified header to extract kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise AuthenticationFailed("Invalid token header")

            # 2️⃣ Fetch JWKS
            jwks = requests.get(
                f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json",
                timeout=5
            ).json()

            # 3️⃣ Find matching key
            public_key = None
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    public_key = jwk.construct(key)
                    break

            if public_key is None:
                raise AuthenticationFailed("Public key not found")

            # 4️⃣ Decode & verify token
            payload = jwt.decode(
                token,
                public_key.to_pem().decode("utf-8"),
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )

            # 5️⃣ Attach stable Auth0 user id
            request.auth0_user_id = payload.get("sub")

            if not request.auth0_user_id:
                raise AuthenticationFailed("auth0_user_id missing in token")

            return True

        except Exception as e:
            print("AUTH0 AUTH ERROR:", e)
            raise AuthenticationFailed("Invalid or expired token")
