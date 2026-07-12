"""Custom DRF exception handler producing a uniform error envelope.

Wired via ``REST_FRAMEWORK["EXCEPTION_HANDLER"]`` in settings, so every DRF view returns errors
in the same shape.
"""

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Wrap DRF's default error output in a consistent ``{"error": {...}}`` envelope.

    Args:
        exc: The exception raised while processing the request.
        context: DRF context (view, request, args) for the failing call.

    Returns:
        The augmented ``Response``, or ``None`` if DRF does not handle the exception
        (letting Django render a 500).
    """
    response = exception_handler(exc, context)
    if response is None:
        return None

    response.data = {
        "error": {
            "status_code": response.status_code,
            "detail": response.data,
        }
    }
    return response
