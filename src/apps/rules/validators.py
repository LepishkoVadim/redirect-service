"""Validators guarding the redirect target against open-redirect abuse."""

from urllib.parse import urlparse

from django.core.exceptions import ValidationError

ALLOWED_SCHEMES = ("http", "https")


def validate_redirect_scheme(value: str) -> None:
    """Reject redirect URLs whose scheme is not http/https.

    Blocks dangerous schemes such as ``javascript:``, ``data:`` and ``file:`` that could
    turn a stored redirect into an XSS or local-file vector.

    Args:
        value: The candidate redirect URL.

    Raises:
        ValidationError: If the URL scheme is not in the http/https allowlist.
    """
    scheme = urlparse(value).scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise ValidationError(
            "Only http and https redirect URLs are allowed.",
            code="invalid_scheme",
        )