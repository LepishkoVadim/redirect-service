"""Abstract model bases reused across apps (UUID primary key, created/modified stamps)."""

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Abstract base giving a non-editable UUID primary key.

    UUIDs are non-enumerable, so exposing a rule's ``id`` in the API leaks no ordering or count.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract base adding auto-managed ``created`` / ``modified`` timestamps."""

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
