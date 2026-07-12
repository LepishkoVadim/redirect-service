"""RedirectRule CRUD viewset (owner-scoped, JWT-secured)."""

from typing import cast

import structlog
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from apps.rules.api.serializers import RedirectRuleSerializer
from apps.rules.models import RedirectRule
from apps.rules.permissions import IsOwner
from apps.rules.services import create_rule
from apps.users.models import User

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List your redirect rules", tags=["rules"]),
    create=extend_schema(summary="Create a redirect rule", tags=["rules"]),
    retrieve=extend_schema(summary="Retrieve one of your rules", tags=["rules"]),
    partial_update=extend_schema(summary="Update one of your rules", tags=["rules"]),
    destroy=extend_schema(summary="Delete one of your rules", tags=["rules"]),
)
class RedirectRuleViewSet(ModelViewSet[RedirectRule]):
    """List/create/retrieve/update/delete the requesting user's redirect rules.

    The queryset is scoped to ``request.user``, so another user's rule is never found
    (404, not 403). ``PUT`` is disabled — updates are PATCH-only.
    """

    serializer_class = RedirectRuleSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    # Class-level queryset lets drf-spectacular derive the UUID `id` path param;
    # runtime access is owner-scoped via get_queryset() below.
    queryset = RedirectRule.objects.all()
    # No PUT: partial updates only.
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet[RedirectRule]:
        """Return only the rules owned by the current user."""
        user = cast(User, self.request.user)
        return RedirectRule.objects.filter(created_by=user)

    def perform_create(self, serializer: BaseSerializer[RedirectRule]) -> None:
        """Create the rule via the service (owner = request user, autogen identifier)."""
        user = cast(User, self.request.user)
        serializer.instance = create_rule(
            user=user,
            redirect_url=serializer.validated_data["redirect_url"],
            is_private=serializer.validated_data.get("is_private", False),
        )

    def perform_update(self, serializer: BaseSerializer[RedirectRule]) -> None:
        """Persist an update and log it."""
        rule = serializer.save()
        logger.info("rule.updated", rule_id=str(rule.id), owner_id=self.request.user.pk)

    def perform_destroy(self, instance: RedirectRule) -> None:
        """Delete a rule and log it."""
        rule_id = str(instance.id)
        instance.delete()
        logger.info("rule.deleted", rule_id=rule_id, owner_id=self.request.user.pk)