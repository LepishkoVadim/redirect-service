"""Shared pytest fixtures.

Auth uses ``RefreshToken.for_user`` to set a Bearer header directly, avoiding the token
endpoint so tests never trip its rate limit.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.rules.models import RedirectRule
from apps.rules.services import create_rule

User = get_user_model()


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the Redis-backed cache (throttle counters) around every test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    """An unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """A regular user (rule owner in most tests)."""
    return User.objects.create_user("alice", "alice@example.com", "pass12345")


@pytest.fixture
def other_user(db):
    """A second user, used for ownership / any-authenticated checks."""
    return User.objects.create_user("bob", "bob@example.com", "pass12345")


def _client_for(user):
    client = APIClient()
    access = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@pytest.fixture
def auth_client(user):
    """API client authenticated as ``user`` via a Bearer JWT."""
    return _client_for(user)


@pytest.fixture
def other_client(other_user):
    """API client authenticated as ``other_user`` via a Bearer JWT."""
    return _client_for(other_user)


@pytest.fixture
def rule(user) -> RedirectRule:
    """A public redirect rule owned by ``user``."""
    return create_rule(user=user, redirect_url="https://example.com/target", is_private=False)


@pytest.fixture
def private_rule(user) -> RedirectRule:
    """A private redirect rule owned by ``user``."""
    return create_rule(user=user, redirect_url="https://example.com/secret", is_private=True)
