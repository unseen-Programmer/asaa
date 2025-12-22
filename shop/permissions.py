from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from jose import jwt  # ✅ use jose for consistency
from django.conf import settings


class IsAuthenticatedWithAuth0(BasePermission):
    def has_permission(self, request, view):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing")

        token = auth.split(" ")[1]

        try:
            decoded = jwt.decode(
                token,
                key=None,  # signature intentionally skipped
                options={
                    "verify_signature": False,
                    "verify_aud": True,
                    "verify_iss": True,
                },
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
                algorithms=["RS256"],
            )
        except Exception:
            raise AuthenticationFailed("Invalid token")

        # 🔥 critical line (kept)
        request.auth0_user_id = decoded.get("sub")

        if not request.auth0_user_id:
            raise AuthenticationFailed("auth0_user_id missing in token")

        return True
