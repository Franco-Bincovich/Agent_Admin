"""
Tests extendidos de autenticación: refresh, logout, tokens expirados, validación.
"""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import bcrypt
import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from config.settings import get_settings
from main import app
from services.auth_service import ALGORITHM, create_access_token, hash_password
from services.token_service import create_refresh_token

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())
_EMAIL = "test@example.com"

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": _EMAIL,
    "username": "testuser",
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


# ── Refresh token ───────────────────────────────────────────────────────────


async def test_refresh_with_valid_token_rotates(client):
    """POST /auth/refresh con refresh_token válido devuelve nuevos tokens (rotación)."""
    # Construyo un refresh token real y su hash para que el lookup en DB matchee.
    with patch("repositories.token_repo.save",
               return_value={"id": "tok-1", "user_id": _USER_ID}):
        refresh = await create_refresh_token(_USER_ID)
    token_hash = bcrypt.hashpw(refresh.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    stored = {"id": "tok-1", "user_id": _USER_ID, "token_hash": token_hash}

    with patch("services.token_service.token_repo.find_by_user", return_value=stored), \
         patch("services.token_service.token_repo.delete"), \
         patch("services.token_service._find_user", return_value=_USER), \
         patch("repositories.token_repo.save",
               return_value={"id": "tok-2", "user_id": _USER_ID}):
        resp = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": refresh},
        )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


async def test_refresh_with_invalid_token(client):
    """POST /auth/refresh con refresh_token inválido devuelve 401."""
    resp = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": "not-a-valid-jwt"},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


async def test_refresh_with_access_token_returns_401(client):
    """POST /auth/refresh con un access_token (type=access) devuelve 401."""
    access = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": access},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


async def test_refresh_without_token(client):
    """POST /auth/refresh sin cookie devuelve 401."""
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


# ── Logout ──────────────────────────────────────────────────────────────────


async def test_logout_invalidates_refresh_token(client):
    """POST /auth/logout autenticado invoca delete_all_by_user (revoca tokens en DB)."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.token_service.token_repo.delete_all_by_user") as mock_delete:
        resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    mock_delete.assert_called_once_with(_USER_ID)


async def test_logout_without_token(client):
    """POST /auth/logout sin token devuelve 401."""
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


# ── Token expirado ──────────────────────────────────────────────────────────


async def test_protected_endpoint_with_expired_token(client):
    """Endpoint protegido con token expirado devuelve 401 con mensaje genérico."""
    settings = get_settings()
    payload = {
        "sub": _USER_ID,
        "role": "editor",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
        "iat": datetime.now(timezone.utc) - timedelta(minutes=70),
        "type": "access",
    }
    expired = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == "UNAUTHORIZED"
    # Mensaje genérico — no revela que el token expiró
    assert "expir" not in body["message"].lower()


# ── Registro: validación de payload ──────────────────────────────────────────


async def test_register_password_too_short(client):
    """Registro con password < 8 chars devuelve 422."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "nuevo@example.com",
            "password": "short",
            "nombre": "Nuevo User",
            "rol": "editor",
        },
    )
    assert resp.status_code == 422


async def test_register_invalid_email(client):
    """Registro con email inválido devuelve 422."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "no-es-email",
            "password": "Password123!",
            "nombre": "Nuevo User",
            "rol": "editor",
        },
    )
    assert resp.status_code == 422


async def test_register_missing_fields(client):
    """Registro con campos faltantes devuelve 422."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "incompleto@example.com"},
    )
    assert resp.status_code == 422
