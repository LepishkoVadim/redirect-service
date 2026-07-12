"""Object-level ownership permission for redirect rules."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import RedirectRule


class IsOwner(BasePermission):
    """Allow access to a rule only to the user who created it.

    Combined with a queryset already filtered to ``request.user``, a foreign object is
    never fetched — so the caller sees a 404, not a 403 (existence is not leaked).
    """

    def has_object_permission(self, request: Request, view: APIView, obj: RedirectRule) -> bool:
        """Return True only when the requesting user owns ``obj``."""
        return bool(obj.created_by_id == request.user.pk)