"""
Tests del log de actividad: historial unificado de generaciones y documentos.
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token, hash_password

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": "test@example.com",
    "password_hash": hash_password(_PASSWORD),
    "rol": "editor",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}

_GEN_RECORD = {
    "id": str(uuid.uuid4()),
    "usuario_id": _USER_ID,
    "objetivo": "Objetivo X",
    "estado": "listo",
    "pptx_url": "https://test.supabase.co/x.pptx",
    "gamma_url": None,
    "pptx_gamma_url": None,
    "slides_count": 5,
    "creado_en": datetime.utcnow().isoformat(),
}

_DOC_RECORD = {
    "id": str(uuid.uuid4()),
    "usuario_id": _USER_ID,
    "estado": "listo",
    "creado_en": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_get_activity_authenticated(client):
    """GET /activity devuelve historial unificado del usuario autenticado."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.activity_service.generation_repo.find_by_user",
               return_value=[_GEN_RECORD]), \
         patch("services.activity_service.documento_repo.find_by_user",
               return_value=[_DOC_RECORD]):
        resp = await client.get(
            "/api/v1/activity",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    tipos = {item["tipo"] for item in body}
    assert tipos == {"presentacion", "documento"}


async def test_get_activity_without_token(client):
    """GET /activity sin token devuelve 401."""
    resp = await client.get("/api/v1/activity")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


async def test_activity_records_for_successful_generation(client):
    """Una generación exitosa aparece en /activity como tipo='presentacion'."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.activity_service.generation_repo.find_by_user",
               return_value=[_GEN_RECORD]) as mock_gen, \
         patch("services.activity_service.documento_repo.find_by_user",
               return_value=[]):
        resp = await client.get(
            "/api/v1/activity",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    mock_gen.assert_called_once_with(_USER_ID)
    body = resp.json()
    assert len(body) == 1
    assert body[0]["tipo"] == "presentacion"


async def test_activity_limit_query_param_does_not_break(client):
    """Query param ?limit=5 no rompe el endpoint (ignorado, no soportado actualmente)."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.activity_service.generation_repo.find_by_user", return_value=[]), \
         patch("services.activity_service.documento_repo.find_by_user", return_value=[]):
        resp = await client.get(
            "/api/v1/activity?limit=5",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200


async def test_activity_isolated_by_user(client):
    """La actividad de un usuario no incluye registros de otro usuario."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.activity_service.generation_repo.find_by_user",
               return_value=[]) as mock_gen, \
         patch("services.activity_service.documento_repo.find_by_user",
               return_value=[]) as mock_doc:
        resp = await client.get(
            "/api/v1/activity",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    # Confirma que el lookup usa el ID del usuario autenticado, no otros.
    mock_gen.assert_called_once_with(_USER_ID)
    mock_doc.assert_called_once_with(_USER_ID)
    assert resp.json() == []
