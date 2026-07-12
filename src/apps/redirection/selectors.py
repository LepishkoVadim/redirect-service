"""Read-side resolution of redirect identifiers to rules.

``resolve_public`` filters to public rules so a private rule is never exposed through the
public endpoint — existence is not leaked. ``resolve_private`` (authenticated endpoint)
resolves any rule: private ones plus public ones as a fallback.
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
    """Resolve a redirect identifier for the authenticated endpoint.

    No ownership check — per the spec, any authenticated user may follow a private redirect.
    Also falls back to public rules, so an authenticated user can follow any redirect.

    Args:
        identifier: The rule's ``redirect_identifier``.

    Returns:
        The matching RedirectRule (private or public).

    Raises:
        Http404: If no rule has this identifier.
    """
    try:
        rule = RedirectRule.objects.get(redirect_identifier=identifier)
    except RedirectRule.DoesNotExist:
        logger.info("redirect.private_miss", identifier=identifier)
        raise Http404 from None
    logger.info("redirect.private_hit", identifier=identifier, rule_id=str(rule.id),
                private=rule.is_private)
    return rule