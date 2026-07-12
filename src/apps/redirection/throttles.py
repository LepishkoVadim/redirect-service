"""IP-based throttling for the public redirect endpoint (flood defense)."""

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView


class PublicRedirectThrottle(SimpleRateThrottle):
    """Rate-limit public redirects by client IP under the ``public_redirect`` scope.

    Rate from ``REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["public_redirect"]`` (env
    ``THROTTLE_PUBLIC_REDIRECT``). Only the public endpoint is throttled; private + CRUD are not.
    """

    scope = "public_redirect"

    def get_cache_key(self, request: Request, view: APIView) -> str | None:
        """Key the bucket on the client IP.

        ``get_ident`` honors ``X-Forwarded-For`` per the ``NUM_PROXIES`` setting, so behind
        nginx (``DJANGO_NUM_PROXIES=1``) this keys on the real client, not the proxy.
        """
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}