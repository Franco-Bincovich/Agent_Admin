"""
Tests de flujos críticos — Agent Admin Backend.
Base 9 (BASES-DE-DESARROLLO.md): flujos que sostienen el negocio no se rompen silenciosamente.

Estrategia de mock: se parchean las funciones del repositorio al nivel del módulo controller
(donde fueron importadas con `from repositories.user_repo import ...`) para evitar
cualquier conexión real a Supabase durante los tests.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

# conftest.py ya seteó las variables de entorno antes de este import.
from main import app
from services.auth_service import create_access_token, hash_password

# ── Datos fijos de prueba ────────────────────────────────────────────────────

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

# ── Fixture: cliente HTTP contra la app ASGI en memoria ─────────────────────


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
    with patch("controllers.auth_controller.find_by_email", return_value=None), \
         patch("controllers.auth_controller.create", return_value=_USER):
        resp = await client.post("/api/v1/auth/register", json={
            "email": _EMAIL,
            "password": _PASSWORD,
            "nombre": "Test User",
            "rol": "editor",
        })
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


# ── 3. Registro con email duplicado ─────────────────────────────────────────


async def test_register_duplicate_email(client):
    with patch("controllers.auth_controller.find_by_email", return_value=_USER):
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
    with patch("controllers.auth_controller.find_by_email", return_value=_USER):
        resp = await client.post("/api/v1/auth/login", json={
            "email": _EMAIL,
            "password": _PASSWORD,
        })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


# ── 5. Login con password incorrecto ─────────────────────────────────────────


async def test_login_wrong_password(client):
    with patch("controllers.auth_controller.find_by_email", return_value=_USER):
        resp = await client.post("/api/v1/auth/login", json={
            "email": _EMAIL,
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
    with patch("controllers.auth_controller.find_by_id", return_value=_USER):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == _EMAIL
    assert body["rol"] == "editor"


# ── 8. Crear generación sin autenticación ───────────────────────────────────


async def test_create_generation_unauthorized(client):
    # El middleware rechaza antes de que llegue a validar el cuerpo multipart.
    resp = await client.post("/api/v1/generations/")
    assert resp.status_code == 401
    assert resp.json()["error"] is True
