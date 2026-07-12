"""Custom user model.

Declared up front (before the first migration) so the project owns its user table and
can extend it later without a painful swap. It currently adds nothing beyond
``AbstractUser`` — the extension point is the point.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Project user; created only via the Django admin (no self-registration)."""