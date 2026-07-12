"""Tests for JWT token endpoints (retrieve, refresh, logout, throttle, inactive user)."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def account(db):
    return User.objects.create_user("carol", "carol@example.com", "pass12345")


@pytest.mark.django_db
def test_retrieve_token_ok(api_client, account):
    resp = api_client.post(
        "/retrieve-token/", {"username": "carol", "password": "pass12345"}, format="json"
    )
    assert resp.status_code == 200
    assert "access" in resp.json() and "refresh" in resp.json()


@pytest.mark.django_db
def test_retrieve_token_bad_credentials(api_client, account):
    resp = api_client.post(
        "/retrieve-token/", {"username": "carol", "password": "wrong"}, format="json"
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_inactive_user_cannot_get_token(api_client, account):
    account.is_active = False
    account.save()
    resp = api_client.post(
        "/retrieve-token/", {"username": "carol", "password": "pass12345"}, format="json"
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_refresh_rotation_blacklists_old(api_client, account):
    tokens = api_client.post(
        "/retrieve-token/", {"username": "carol", "password": "pass12345"}, format="json"
    ).json()
    old_refresh = tokens["refresh"]

    first = api_client.post("/refresh-token/", {"refresh": old_refresh}, format="json")
    assert first.status_code == 200

    # Old refresh was blacklisted on rotation → reuse rejected.
    reuse = api_client.post("/refresh-token/", {"refresh": old_refresh}, format="json")
    assert reuse.status_code == 401


@pytest.mark.django_db
def test_logout_blacklists_refresh(api_client, account):
    tokens = api_client.post(
        "/retrieve-token/", {"username": "carol", "password": "pass12345"}, format="json"
    ).json()
    refresh = tokens["refresh"]

    assert api_client.post("/logout/", {"refresh": refresh}, format="json").status_code == 200
    reuse = api_client.post("/refresh-token/", {"refresh": refresh}, format="json")
    assert reuse.status_code == 401


@pytest.mark.django_db
def test_token_endpoint_throttled(api_client, account):
    # Rate is 10/min; the 11th attempt in the window is rejected.
    codes = [
        api_client.post(
            "/retrieve-token/", {"username": "carol", "password": "pass12345"}, format="json"
        ).status_code
        for _ in range(12)
    ]
    assert 429 in codes
