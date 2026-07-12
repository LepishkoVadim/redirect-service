"""Tests for public/private redirect resolution (302/404, auth, HEAD)."""

import pytest


@pytest.mark.django_db
def test_public_redirect_302(api_client, rule):
    resp = api_client.get(f"/redirect/public/{rule.redirect_identifier}/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == rule.redirect_url


@pytest.mark.django_db
def test_private_rule_via_public_is_404(api_client, private_rule):
    resp = api_client.get(f"/redirect/public/{private_rule.redirect_identifier}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_public_rule_via_private_302(auth_client, rule):
    # Authenticated users may follow public rules through the private endpoint (fallback).
    resp = auth_client.get(f"/redirect/private/{rule.redirect_identifier}/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == rule.redirect_url


@pytest.mark.django_db
def test_private_redirect_requires_auth(api_client, private_rule):
    resp = api_client.get(f"/redirect/private/{private_rule.redirect_identifier}/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_private_redirect_any_authenticated_user(other_client, private_rule):
    # other_user does not own the rule but is authenticated → allowed.
    resp = other_client.get(f"/redirect/private/{private_rule.redirect_identifier}/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == private_rule.redirect_url


@pytest.mark.django_db
def test_head_public_redirect_302(api_client, rule):
    resp = api_client.head(f"/redirect/public/{rule.redirect_identifier}/")
    assert resp.status_code == 302


@pytest.mark.django_db
def test_missing_identifier_404(api_client):
    assert api_client.get("/redirect/public/does-not-exist/").status_code == 404
