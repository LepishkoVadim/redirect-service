"""Throttling for the token endpoints (anti brute-force)."""

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView


class TokenScopedThrottle(SimpleRateThrottle):
    """Rate-limit token issuance/refresh by client IP under the ``token`` scope.

    The rate comes from ``REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["token"]`` (env
    ``THROTTLE_TOKEN``). A ``SimpleRateThrottle`` (not ``ScopedRateThrottle``) is used so
    the fixed ``scope`` works without requiring a ``throttle_scope`` attribute on each view.
    Applied only to public token endpoints — CRUD and private redirects stay unthrottled.
    """

    scope = "token"

    def get_cache_key(self, request: Request, view: APIView) -> str | None:
        """Key the throttle bucket on the requesting client's IP."""
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}