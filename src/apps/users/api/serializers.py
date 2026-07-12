"""Token serializers — thin wrappers over SimpleJWT for naming + future customization.

SimpleJWT already rejects inactive users and bad credentials, so these add no logic yet;
they exist as the project's own extension point and give the schema stable names.
"""

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)


class RetrieveTokenSerializer(TokenObtainPairSerializer):
    """Validate username/password and issue an access + refresh pair."""


class RefreshTokenSerializer(TokenRefreshSerializer):
    """Exchange a valid refresh token for a new access token."""