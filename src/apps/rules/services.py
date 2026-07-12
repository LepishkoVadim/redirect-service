"""Business logic for redirect rules (identifier generation + creation)."""

import structlog
from django.db import IntegrityError, transaction
from nanoid import generate

from apps.users.models import User

from .models import RedirectRule

logger = structlog.get_logger(__name__)

_IDENTIFIER_SIZE = 12
_MAX_RETRIES = 5


class IdentifierCollisionError(Exception):
    """Raised when a unique identifier could not be generated within the retry budget."""


def generate_identifier() -> str:
    """Return a short URL-safe identifier for a redirect rule."""
    return str(generate(size=_IDENTIFIER_SIZE))


def create_rule(*, user: User, redirect_url: str, is_private: bool = False) -> RedirectRule:
    """Create a RedirectRule with a unique nanoid identifier.

    Retries a bounded number of times on identifier collision; the database unique
    constraint on ``redirect_identifier`` is the final source of truth.

    Args:
        user: Owner of the rule (``request.user``).
        redirect_url: Target URL; must pass the http/https scheme allowlist.
        is_private: If True, the rule is resolvable only by authenticated users.

    Returns:
        The persisted RedirectRule instance.

    Raises:
        IdentifierCollisionError: If no unique identifier is found within the retry budget.
    """
    for attempt in range(1, _MAX_RETRIES + 1):
        identifier = generate_identifier()
        try:
            with transaction.atomic():
                rule = RedirectRule.objects.create(
                    redirect_url=redirect_url,
                    is_private=is_private,
                    redirect_identifier=identifier,
                    created_by=user,
                )
        except IntegrityError:
            # Extremely unlikely at this identifier length; retry with a fresh one.
            logger.warning("rule.identifier_collision", attempt=attempt, identifier=identifier)
            continue
        logger.info(
            "rule.created",
            rule_id=str(rule.id),
            owner_id=user.pk,
            is_private=is_private,
        )
        return rule

    raise IdentifierCollisionError(
        f"Could not generate a unique identifier after {_MAX_RETRIES} attempts."
    )