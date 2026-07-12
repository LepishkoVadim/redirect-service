"""Redirect endpoints: resolve an identifier and issue a 302 to the target URL."""

from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.redirection.selectors import resolve_private, resolve_public
from apps.redirection.throttles import PublicRedirectThrottle

_REDIRECT_RESPONSES = {
    302: OpenApiResponse(description="Redirect to the rule's target URL."),
    404: OpenApiResponse(description="No matching rule for this identifier."),
}


class PublicRedirectView(APIView):
    """Resolve a public identifier and 302-redirect to its target (open, IP-throttled)."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PublicRedirectThrottle]

    @extend_schema(summary="Follow a public redirect", tags=["redirect"],
                   responses=_REDIRECT_RESPONSES)
    def get(self, request: Request, identifier: str) -> HttpResponseRedirect:
        """Return a 302 to the public rule's target, or 404 if none."""
        rule = resolve_public(identifier)
        # 302 (not 301): the target is mutable, so browsers must not cache the redirect.
        return HttpResponseRedirect(rule.redirect_url)

    @extend_schema(exclude=True)
    def head(self, request: Request, identifier: str) -> HttpResponseRedirect:
        """Support ``curl -I`` (HEAD) with the same resolution as GET."""
        return self.get(request, identifier)


class PrivateRedirectView(APIView):
    """Resolve any identifier and 302-redirect (authenticated; private + public fallback)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Follow a private redirect", tags=["redirect"],
                   responses=_REDIRECT_RESPONSES)
    def get(self, request: Request, identifier: str) -> HttpResponseRedirect:
        """Return a 302 to the private rule's target, or 404 if none."""
        rule = resolve_private(identifier)
        return HttpResponseRedirect(rule.redirect_url)

    @extend_schema(exclude=True)
    def head(self, request: Request, identifier: str) -> HttpResponseRedirect:
        """Support ``curl -I`` (HEAD) with the same resolution as GET."""
        return self.get(request, identifier)