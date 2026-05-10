"""
Tests de autenticación — registro, login, endpoints protegidos.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token, hash_password

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())
_EMAIL = "test@example.com"

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": _EMAIL,
    "password_hash": hash_password(_PASSWORD),
    "rol": "editor",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── 1. Health ────────────────────────────────────────────────────────────────


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── 2. Registro exitoso ──────────────────────────────────────────────────────


async def test_register_success(client):
    with patch("services.auth_service.find_by_email", return_value=None), \
         patch("services.auth_service.create_user_record", return_value=_USER), \
         patch("repositories.token_repo.save", return_value={"id": "tok-1", "user_id": _USER_ID}):
        resp = await client.post("/api/v1/auth/register", json={
            "email": _EMAIL,
            "password": _PASSWORD,
            "nombre": "Test User",
            "rol": "editor",
        })
    assert resp.status_code == 201
    assert resp.json() == {"ok": True}
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


# ── 3. Registro con email duplicado ─────────────────────────────────────────


async def test_register_duplicate_email(client):
    with patch("services.auth_service.find_by_email", return_value=_USER):
        resp = await client.post("/api/v1/auth/register", json={
            "email": _EMAIL,
            "password": _PASSWORD,
            "nombre": "Otro User",
            "rol": "editor",
        })
    assert resp.status_code == 409
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "USER_ALREADY_EXISTS"


# ── 4. Login con credenciales correctas ─────────────────────────────────────


async def test_login_success(client):
    with patch("services.auth_service.find_by_username", return_value=_USER), \
         patch("repositories.token_repo.save", return_value={"id": "tok-1", "user_id": _USER_ID}):
        resp = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": _PASSWORD,
        })
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


# ── 5. Login con password incorrecto ─────────────────────────────────────────


async def test_login_wrong_password(client):
    with patch("services.auth_service.find_by_username", return_value=_USER):
        resp = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrong-password-that-does-not-match",
        })
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "UNAUTHORIZED"


# ── 6. Endpoint protegido sin token ─────────────────────────────────────────


async def test_protected_endpoint_without_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


# ── 7. Endpoint protegido con token válido ───────────────────────────────────


async def test_protected_endpoint_with_token(client):
    token = create_access_token(_USER_ID, "editor")
    with patch("services.auth_service.find_by_id", return_value=_USER):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == _EMAIL
    assert body["rol"] == "editor"
