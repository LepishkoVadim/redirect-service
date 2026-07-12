"""Redirect routes (root-level, matching the examples)."""

from django.urls import path

from apps.redirection.api.views import PrivateRedirectView, PublicRedirectView

urlpatterns = [
    path("redirect/public/<str:identifier>/", PublicRedirectView.as_view(), name="redirect-public"),
    path(
        "redirect/private/<str:identifier>/",
        PrivateRedirectView.as_view(),
        name="redirect-private",
    ),
]