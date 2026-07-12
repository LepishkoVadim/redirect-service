"""Root URLconf.

Everything is mounted at the root (no ``/api/v1/`` prefix) to match the curl examples:
- ``/`` — 302 to the Swagger UI (a friendly landing page);
- ``/admin/`` — Django admin (the only way users are created);
- ``/health/`` — liveness probe (``apps.common``);
- token endpoints ``/retrieve-token/``, ``/refresh-token/``, ``/logout/`` (``apps.users``);
- ``/url/`` CRUD (``apps.rules``) and ``/redirect/{public,private}/<id>/`` (``apps.redirection``);
- ``/api/schema/`` + ``/api/docs/`` — OpenAPI schema and Swagger UI (drf-spectacular).
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Landing: send the bare root to the API docs (302, resolved at request time).
    path("", RedirectView.as_view(pattern_name="swagger-ui", permanent=False), name="root"),
    path("admin/", admin.site.urls),
    path("", include("apps.common.urls")),
    path("", include("apps.users.api.urls")),
    path("", include("apps.rules.api.urls")),
    path("", include("apps.redirection.api.urls")),
    # API schema + Swagger UI.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
