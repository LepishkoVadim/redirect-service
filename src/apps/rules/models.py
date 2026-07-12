"""The RedirectRule model — a user-owned public/private redirect target."""

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.rules.validators import validate_redirect_scheme


class RedirectRule(UUIDModel, TimeStampedModel):
    """A redirect rule resolved by its short ``redirect_identifier``.

    Public rules resolve for anyone; private rules require an authenticated caller.
    Only the creator may edit or delete a rule. The ``id`` (UUID) and ``created`` / ``modified``
    timestamps are inherited from ``UUIDModel`` / ``TimeStampedModel``.
    """

    redirect_url = models.URLField(validators=[validate_redirect_scheme])
    is_private = models.BooleanField(default=False)
    # Set by rules.services.create_rule (nanoid); never client-supplied.
    redirect_identifier = models.CharField(max_length=32, unique=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rules",
    )

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["created_by", "-created"])]

    def __str__(self) -> str:
        """Return a short human label for admin/logs."""
        return f"{self.redirect_identifier} → {self.redirect_url}"