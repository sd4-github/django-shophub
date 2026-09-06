# =============================================================================
# users/tests.py  --  pytest tests for registration + JWT auth
# =============================================================================
# Interview concepts demonstrated:
#   * DRF APIClient + force_authenticate (simulate JWT without minting tokens)
#   * Serializer validation: email uniqueness, password write_only
#   * Authentication enforcement: unauthenticated requests return 401/403
#   * Custom User model: create_user via the manager (password is hashed)
#
# Run with:  .venv/bin/pytest users/ -v

import pytest
from django.contrib.auth import get_user_model

# get_user_model() returns our custom User (email-based login), not the
# default Django User. Always use this — never import User directly.
User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures (pytest-django)
# ---------------------------------------------------------------------------
@pytest.fixture
def api_client():
    """DRF's test client: sends requests without starting a real server."""
    from rest_framework.test import APIClient
    return APIClient()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_register_creates_user(api_client):
    """POST /api/users/register/ should:
       1. Create a User row in the DB.
       2. Hash the password (never store plaintext).
       3. Never return the password in the response (write_only field)."""
    r = api_client.post("/api/users/register/", {
        "email": "new@example.com", "password": "secret123"
    }, format="json")
    assert r.status_code == 201                             # HTTP 201 Created
    assert User.objects.filter(email="new@example.com").exists()  # row exists
    assert "password" not in r.data                         # password NEVER leaked
    u = User.objects.get(email="new@example.com")
    assert not u.check_password("wrong")                    # wrong password fails
    assert u.check_password("secret123")                    # correct password works


@pytest.mark.django_db
def test_duplicate_email_rejected(api_client):
    """Registering with an already-used email must return 400.
       The RegisterSerializer.validate_email() hook checks uniqueness."""
    User.objects.create_user(email="dup@example.com", password="pw12345")
    r = api_client.post("/api/users/register/", {
        "email": "dup@example.com", "password": "secret123"
    }, format="json")
    assert r.status_code == 400


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    """GET /api/users/me/ without a token must be rejected.
       DRF's default permission_classes = [IsAuthenticated] enforces this."""
    r = api_client.get("/api/users/me/")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_me_returns_user(api_client):
    """GET /api/users/me/ with a valid token returns the authenticated user.
       force_authenticate() bypasses JWT minting — useful in tests."""
    user = User.objects.create_user(email="me@example.com", password="pw12345")
    api_client.force_authenticate(user)                     # inject user into request
    r = api_client.get("/api/users/me/")
    assert r.status_code == 200
    assert r.data["email"] == "me@example.com"
