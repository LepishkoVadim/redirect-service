"""Read-side resolution of redirect identifiers to rules.

Both selectors raise ``Http404`` for a miss so a private rule is never exposed through the
public endpoint (and vice-versa) — existence is not leaked.
"""

import structlog
from django.http import Http404

from apps.rules.models import RedirectRule

logger = structlog.get_logger(__name__)


def resolve_public(identifier: str) -> RedirectRule:
    """Resolve a public redirect identifier.

    Args:
        identifier: The rule's ``redirect_identifier``.

    Returns:
        The matching public RedirectRule.

    Raises:
        Http404: If no public rule has this identifier.
    """
    try:
        rule = RedirectRule.objects.get(redirect_identifier=identifier, is_private=False)
    except RedirectRule.DoesNotExist:
        logger.info("redirect.public_miss", identifier=identifier)
        raise Http404 from None
    logger.info("redirect.public_hit", identifier=identifier, rule_id=str(rule.id))
    return rule


def resolve_private(identifier: str) -> RedirectRule:
    """Resolve a private redirect identifier (caller must be authenticated).

    No ownership check — per the spec, any authenticated user may follow a private redirect.

    Args:
        identifier: The rule's ``redirect_identifier``.

    Returns:
        The matching private RedirectRule.

    Raises:
        Http404: If no private rule has this identifier.
    """
    try:
        rule = RedirectRule.objects.get(redirect_identifier=identifier, is_private=True)
    except RedirectRule.DoesNotExist:
        logger.info("redirect.private_miss", identifier=identifier)
        raise Http404 from None
    logger.info("redirect.private_hit", identifier=identifier, rule_id=str(rule.id))
    return rule