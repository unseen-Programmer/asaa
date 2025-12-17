from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from .utils.auth0 import get_token_from_header, verify_auth0_token


class IsAuthenticatedWithAuth0(BasePermission):
    """
    Allows access only to requests with a valid Auth0 JWT.
    """

    def has_permission(self, request, view):
        try:
            token = get_token_from_header(request)
            payload = verify_auth0_token(token)

            # Attach Auth0 user info to request
            request.auth = payload               # DRF standard
            request.auth0_user = payload
            request.auth0_user_id = payload.get("sub")

            return True

        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Authentication failed")
