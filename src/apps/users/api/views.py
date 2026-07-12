"""Token endpoints: issue (retrieve), refresh and blacklist (logout) JWTs.

Issue/refresh are rate-limited under the ``token`` scope (anti brute-force). Refresh rotates
the token and blacklists the previous one (see ``SIMPLE_JWT`` in settings).
"""

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.api.serializers import RefreshTokenSerializer, RetrieveTokenSerializer
from apps.users.throttles import TokenScopedThrottle


@extend_schema(summary="Retrieve JWT tokens", tags=["auth"])
class RetrieveTokenView(TokenObtainPairView):
    """POST username + password → access + refresh tokens (throttled)."""

    serializer_class = RetrieveTokenSerializer
    throttle_classes = [TokenScopedThrottle]


@extend_schema(summary="Refresh access token", tags=["auth"])
class RefreshTokenView(TokenRefreshView):
    """POST a refresh token → a fresh access token; old refresh is blacklisted (throttled)."""

    serializer_class = RefreshTokenSerializer
    throttle_classes = [TokenScopedThrottle]


@extend_schema(summary="Log out (blacklist refresh token)", tags=["auth"])
class LogoutView(TokenBlacklistView):
    """POST a refresh token to blacklist it (logout). Requires blacklist app enabled."""

    throttle_classes = [TokenScopedThrottle]