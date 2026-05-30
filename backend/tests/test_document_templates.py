"""
Tests del módulo de plantillas de documentos: CRUD completo + reglas de ownership.
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token, hash_password
from utils.errors import AppError, ErrorCode

_USER_ID = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())
_TEMPLATE_ID = str(uuid.uuid4())

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": "test@example.com",
    "password_hash": hash_password("TestPass123!"),
    "rol": "editor",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}

_NOW = datetime.utcnow().isoformat()

_FAKE_TEMPLATE = {
    "id": _TEMPLATE_ID,
    "usuario_id": _USER_ID,
    "nombre": "Plantilla de prueba",
    "secciones": [
        {"id": "1", "nombre": "introduccion"},
        {"id": "2", "nombre": "desarrollo"},
        {"id": "3", "nombre": "conclusiones"},
    ],
    "is_default": False,
    "creado_en": _NOW,
    "actualizado_en": _NOW,
}

_FAKE_TEMPLATE_DEFAULT = {
    **_FAKE_TEMPLATE,
    "is_default": True,
}

_BASE_URL = "/api/v1/document-templates"

_SVC = "controllers.document_template_controller.document_template_service"


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


# ── Crear plantilla ──────────────────────────────────────────────────────────


async def test_create_template_success(client):
    """POST /document-templates con datos válidos devuelve 201 y la plantilla creada."""
    token = create_access_token(_USER_ID, "editor")
    with patch(f"{_SVC}.create_template", new_callable=AsyncMock, return_value=_FAKE_TEMPLATE):
        resp = await client.post(
            _BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nombre": "Plantilla de prueba",
                "secciones": [
                    {"id": "1", "nombre": "introduccion"},
                    {"id": "2", "nombre": "desarrollo"},
                    {"id": "3", "nombre": "conclusiones"},
                ],
            },
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == _TEMPLATE_ID
    assert body["nombre"] == "Plantilla de prueba"
    assert body["secciones"] == [
        {"id": "1", "nombre": "introduccion"},
        {"id": "2", "nombre": "desarrollo"},
        {"id": "3", "nombre": "conclusiones"},
    ]
    assert body["is_default"] is False


async def test_create_first_template_is_default(client):
    """Primera plantilla de un usuario se marca automáticamente como default."""
    token = create_access_token(_USER_ID, "editor")
    with patch(f"{_SVC}.create_template", new_callable=AsyncMock, return_value=_FAKE_TEMPLATE_DEFAULT):
        resp = await client.post(
            _BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nombre": "Plantilla de prueba",
                "secciones": [
                    {"id": "1", "nombre": "introduccion"},
                    {"id": "2", "nombre": "desarrollo"},
                    {"id": "3", "nombre": "conclusiones"},
                ],
            },
        )
    assert resp.status_code == 201
    assert resp.json()["is_default"] is True


# ── Listar plantillas ────────────────────────────────────────────────────────


async def test_list_templates_only_own(client):
    """GET /document-templates devuelve sólo las plantillas del usuario autenticado."""
    token = create_access_token(_USER_ID, "editor")
    with patch(
        f"{_SVC}.get_user_templates",
        new_callable=AsyncMock,
        return_value=[_FAKE_TEMPLATE],
    ) as mock_list:
        resp = await client.get(
            _BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    mock_list.assert_called_once_with(_USER_ID)
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["usuario_id"] == _USER_ID


# ── Obtener plantilla por ID ─────────────────────────────────────────────────


async def test_get_template_success(client):
    """GET /document-templates/{id} devuelve 200 con los datos correctos."""
    token = create_access_token(_USER_ID, "editor")
    with patch(f"{_SVC}.get_template", new_callable=AsyncMock, return_value=_FAKE_TEMPLATE):
        resp = await client.get(
            f"{_BASE_URL}/{_TEMPLATE_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == _TEMPLATE_ID
    assert body["nombre"] == "Plantilla de prueba"


async def test_get_template_other_user_returns_404(client):
    """GET /document-templates/{id} con ID de otro usuario devuelve 404."""
    token = create_access_token(_USER_ID, "editor")
    other_id = str(uuid.uuid4())
    with patch(
        f"{_SVC}.get_template",
        new_callable=AsyncMock,
        side_effect=AppError(f"Plantilla '{other_id}' no encontrada.", ErrorCode.NOT_FOUND, 404),
    ):
        resp = await client.get(
            f"{_BASE_URL}/{other_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


# ── Actualizar plantilla ─────────────────────────────────────────────────────


async def test_update_template_success(client):
    """PUT /document-templates/{id} devuelve 200 con los datos actualizados."""
    token = create_access_token(_USER_ID, "editor")
    updated = {
        **_FAKE_TEMPLATE,
        "nombre": "Plantilla actualizada",
        "secciones": [
            {"id": "1", "nombre": "introduccion"},
            {"id": "2", "nombre": "cierre"},
        ],
    }
    with patch(f"{_SVC}.update_template", new_callable=AsyncMock, return_value=updated):
        resp = await client.put(
            f"{_BASE_URL}/{_TEMPLATE_ID}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nombre": "Plantilla actualizada",
                "secciones": [
                    {"id": "1", "nombre": "introduccion"},
                    {"id": "2", "nombre": "cierre"},
                ],
                "is_default": False,
            },
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["nombre"] == "Plantilla actualizada"
    assert body["secciones"] == [
        {"id": "1", "nombre": "introduccion"},
        {"id": "2", "nombre": "cierre"},
    ]


# ── Marcar como default ──────────────────────────────────────────────────────


async def test_set_default_template_success(client):
    """PATCH /document-templates/{id}/default devuelve 200 con is_default=True."""
    token = create_access_token(_USER_ID, "editor")
    with patch(
        f"{_SVC}.set_default_template",
        new_callable=AsyncMock,
        return_value=_FAKE_TEMPLATE_DEFAULT,
    ):
        resp = await client.patch(
            f"{_BASE_URL}/{_TEMPLATE_ID}/default",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    assert resp.json()["is_default"] is True


# ── Eliminar plantilla ───────────────────────────────────────────────────────


async def test_delete_template_success(client):
    """DELETE /document-templates/{id} devuelve 204."""
    token = create_access_token(_USER_ID, "editor")
    with patch(f"{_SVC}.delete_template", new_callable=AsyncMock, return_value=None):
        resp = await client.delete(
            f"{_BASE_URL}/{_TEMPLATE_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 204


async def test_delete_template_other_user_returns_404(client):
    """DELETE /document-templates/{id} con ID de otro usuario devuelve 404."""
    token = create_access_token(_USER_ID, "editor")
    other_id = str(uuid.uuid4())
    with patch(
        f"{_SVC}.delete_template",
        new_callable=AsyncMock,
        side_effect=AppError(f"Plantilla '{other_id}' no encontrada.", ErrorCode.NOT_FOUND, 404),
    ):
        resp = await client.delete(
            f"{_BASE_URL}/{other_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


# ── Autenticación ────────────────────────────────────────────────────────────


async def test_create_template_without_token_returns_401(client):
    """POST /document-templates sin token de autenticación devuelve 401."""
    resp = await client.post(
        _BASE_URL,
        json={"nombre": "Sin auth", "secciones": [{"id": "1", "nombre": "intro"}]},
    )
    assert resp.status_code == 401
