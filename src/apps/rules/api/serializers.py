"""Serializer for the RedirectRule resource."""

from rest_framework import serializers

from apps.rules.models import RedirectRule


class RedirectRuleSerializer(serializers.ModelSerializer[RedirectRule]):
    """Serialize/validate RedirectRule for CRUD.

    Server-managed fields (``id``, ``redirect_identifier``, ``created``, ``modified``) are
    read-only; ``created_by`` is set from the request user in the view, never by the client.
    """

    class Meta:
        model = RedirectRule
        fields = [
            "id",
            "redirect_url",
            "is_private",
            "redirect_identifier",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "redirect_identifier", "created", "modified"]