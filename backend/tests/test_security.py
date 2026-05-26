"""
Tests de aspectos críticos de seguridad: headers, payload, rate limiting, CORS.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import hash_password

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": "test@example.com",
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


# ── Headers de seguridad ─────────────────────────────────────────────────────


async def test_security_headers_present(client):
    """Las respuestas incluyen los headers de seguridad estándar."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    headers = {k.lower(): v for k, v in resp.headers.items()}
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert "strict-transport-security" in headers
    assert "referrer-policy" in headers


async def test_server_header_not_revealed(client):
    """El header 'server' (que revelaría el framework) no debe estar presente."""
    resp = await client.get("/health")
    headers = {k.lower(): v for k, v in resp.headers.items()}
    assert "server" not in headers


# ── Payload demasiado grande ────────────────────────────────────────────────


async def test_payload_too_large_returns_413(client):
    """Un Content-Length > 50MB se rechaza con 413 PAYLOAD_TOO_LARGE."""
    huge_size = 51 * 1024 * 1024  # 51 MB
    resp = await client.post(
        "/api/v1/auth/login",
        headers={"Content-Length": str(huge_size), "Content-Type": "application/json"},
        content=b'{"username":"x","password":"y"}',
    )
    assert resp.status_code == 413
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "PAYLOAD_TOO_LARGE"


# ── Rate limiting ───────────────────────────────────────────────────────────


async def test_rate_limit_login_returns_429(client):
    """Tras 5 requests/min al /login, las siguientes devuelven 429 RATE_LIMIT_EXCEEDED."""
    # Reset del limiter para arrancar limpio (el estado persiste entre tests).
    from routers.auth import limiter
    limiter.reset()

    statuses = []
    with patch("services.auth_service.find_by_username", return_value=None):
        for _ in range(8):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"username": "noexiste", "password": "x"},
            )
            statuses.append(resp.status_code)
    # Al menos uno debe ser 429 — confirma que el limiter está activo.
    assert 429 in statuses
    # Limpio para no romper otros tests que usen /login.
    limiter.reset()


# ── Mensajes genéricos de error de autenticación ────────────────────────────


async def test_login_generic_error_for_unknown_user(client):
    """Login con usuario inexistente devuelve UNAUTHORIZED, no USER_NOT_FOUND."""
    from routers.auth import limiter
    limiter.reset()
    with patch("services.auth_service.find_by_username", return_value=None):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "noexisteee", "password": "Password123!"},
        )
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == "UNAUTHORIZED"
    # No revela si fue username inexistente o password incorrecta
    assert "usuario" not in body["message"].lower() or "no" in body["message"].lower()


async def test_login_generic_error_for_wrong_password(client):
    """Login con password incorrecta devuelve el mismo UNAUTHORIZED que usuario inexistente."""
    from routers.auth import limiter
    limiter.reset()
    with patch("services.auth_service.find_by_username", return_value=_USER):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrong-wrong-wrong"},
        )
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == "UNAUTHORIZED"


# ── CORS ────────────────────────────────────────────────────────────────────


async def test_cors_disallowed_origin_not_echoed(client):
    """Origin no permitido no recibe Access-Control-Allow-Origin con su valor."""
    bad_origin = "https://evil.example.com"
    resp = await client.get(
        "/health",
        headers={"Origin": bad_origin},
    )
    # El response no debe ecoar el origen no permitido.
    acao = resp.headers.get("access-control-allow-origin", "")
    assert acao != bad_origin


async def test_cors_allowed_origin_echoed(client):
    """Origin permitido recibe Access-Control-Allow-Origin con su valor."""
    allowed = "http://localhost:3000"
    resp = await client.get(
        "/health",
        headers={"Origin": allowed},
    )
    acao = resp.headers.get("access-control-allow-origin", "")
    assert acao == allowed
