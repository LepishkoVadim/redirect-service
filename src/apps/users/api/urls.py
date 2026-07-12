"""Root-level token endpoints (paths match the examples)."""

from django.urls import path

from apps.users.api.views import LogoutView, RefreshTokenView, RetrieveTokenView

urlpatterns = [
    path("retrieve-token/", RetrieveTokenView.as_view(), name="retrieve-token"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("logout/", LogoutView.as_view(), name="logout"),
]