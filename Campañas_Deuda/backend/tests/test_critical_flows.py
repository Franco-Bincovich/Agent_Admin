"""
Tests críticos del sistema — Campañas de Deuda.

Estos tests cubren los flujos de negocio que no deben romperse silenciosamente
(Base 9 — Testing mínimo obligatorio). Se implementan progresivamente a medida
que avanzan las sesiones.

Mapa de implementación por sesión:
    Sesión 1: health check (este test ya funciona)
    Sesión 3: auth (register, login, logout, endpoint protegido)
    Sesión 4: usuarios y roles
    Sesión 5: carga de cartera
    Sesión 6: creación de ejecución
    Sesión 15: polling de estado de ejecución
"""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app

# ── Sesión 1 ─────────────────────────────────────────────────────────────────


async def test_health_check():
    """El endpoint /health responde 200 OK sin autenticación."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ── Sesión 3 — Auth ───────────────────────────────────────────────────────────


@pytest.mark.skip(reason="Pendiente Sesión 3")
async def test_user_registration_success():
    """Registro exitoso devuelve tokens."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 3")
async def test_user_registration_duplicate_email():
    """Registro con email duplicado devuelve 409."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 3")
async def test_login_success():
    """Login con credenciales válidas devuelve tokens."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 3")
async def test_login_wrong_password():
    """Login con contraseña incorrecta devuelve 401 genérico."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 3")
async def test_protected_endpoint_without_token():
    """Endpoint protegido sin token devuelve 401."""
    raise NotImplementedError


# ── Sesión 4 — Usuarios ───────────────────────────────────────────────────────


@pytest.mark.skip(reason="Pendiente Sesión 4")
async def test_non_admin_cannot_create_user():
    """Un analista no puede crear usuarios (403)."""
    raise NotImplementedError


# ── Sesión 5 — Cartera ────────────────────────────────────────────────────────


@pytest.mark.skip(reason="Pendiente Sesión 5")
async def test_portfolio_upload_success():
    """Subida de archivo CSV válido devuelve 201 con metadatos."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 5")
async def test_portfolio_upload_invalid_type():
    """Subida de tipo no válido devuelve 422."""
    raise NotImplementedError


# ── Sesión 6 — Ejecuciones ────────────────────────────────────────────────────


@pytest.mark.skip(reason="Pendiente Sesión 6")
async def test_execution_create_valid():
    """Combinación válida de dimensiones crea ejecución en estado 'pendiente'."""
    raise NotImplementedError


@pytest.mark.skip(reason="Pendiente Sesión 6")
async def test_execution_create_invalid_period():
    """Período inválido devuelve 422."""
    raise NotImplementedError
