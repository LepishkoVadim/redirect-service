"""Tests for the RedirectRule CRUD endpoints (ownership, readonly, methods, validation)."""

import uuid

import pytest


@pytest.mark.django_db
def test_create_rule(auth_client):
    resp = auth_client.post(
        "/url/", {"redirect_url": "https://google.com", "is_private": False}, format="json"
    )
    assert resp.status_code == 201
    body = resp.json()
    uuid.UUID(body["id"])  # valid UUID
    assert body["redirect_identifier"]


@pytest.mark.django_db
def test_list_is_owner_scoped(auth_client, other_client):
    auth_client.post("/url/", {"redirect_url": "https://a.com"}, format="json")
    assert auth_client.get("/url/").json()["count"] == 1
    # Other user sees none of alice's rules.
    assert other_client.get("/url/").json()["count"] == 0


@pytest.mark.django_db
def test_retrieve_and_patch(auth_client, rule):
    assert auth_client.get(f"/url/{rule.id}/").status_code == 200
    resp = auth_client.patch(f"/url/{rule.id}/", {"is_private": True}, format="json")
    assert resp.status_code == 200
    assert resp.json()["is_private"] is True


@pytest.mark.django_db
def test_readonly_identifier_ignored(auth_client, rule):
    resp = auth_client.patch(
        f"/url/{rule.id}/", {"redirect_identifier": "HACKED"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["redirect_identifier"] == rule.redirect_identifier


@pytest.mark.django_db
def test_put_not_allowed(auth_client, rule):
    resp = auth_client.put(
        f"/url/{rule.id}/", {"redirect_url": "https://x.com", "is_private": False}, format="json"
    )
    assert resp.status_code == 405


@pytest.mark.django_db
def test_ownership_returns_404(other_client, rule):
    assert other_client.get(f"/url/{rule.id}/").status_code == 404
    assert other_client.patch(
        f"/url/{rule.id}/", {"is_private": True}, format="json"
    ).status_code == 404
    assert other_client.delete(f"/url/{rule.id}/").status_code == 404


@pytest.mark.django_db
def test_invalid_scheme_rejected(auth_client):
    resp = auth_client.post(
        "/url/", {"redirect_url": "javascript:alert(1)", "is_private": False}, format="json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_requires_auth(api_client):
    assert api_client.get("/url/").status_code == 401


@pytest.mark.django_db
def test_delete(auth_client, rule):
    assert auth_client.delete(f"/url/{rule.id}/").status_code == 204
