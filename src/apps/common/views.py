"""Health-check endpoint polled by the Docker healthcheck and the CI deploy smoke test."""

from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness/readiness probe: 200 (with a status payload) only when the database answers.

    Open and unthrottled so the container healthcheck and uptime checks can poll it freely.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    @extend_schema(
        summary="Health check",
        description="Returns 200 with a status payload once the database responds to a ping.",
        tags=["health"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "database": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
            }
        },
        examples=[
            OpenApiExample(
                "ok",
                value={
                    "status": "ok",
                    "database": "ok",
                    "timestamp": "2026-07-11T10:00:00Z",
                },
            )
        ],
    )
    def get(self, request: Request) -> Response:
        """Ping the database with ``SELECT 1`` and report status + a server timestamp."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        # Timezone-aware (USE_TZ=True) → serialized as an ISO-8601 string with offset.
        return Response({"status": "ok", "database": "ok", "timestamp": timezone.now()})
