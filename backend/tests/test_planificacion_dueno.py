"""
Tests del endpoint admin-only para asignar el gerente dueño de un área:
PATCH /api/v1/planificacion/{proyecto_id}/areas/{area_id}/dueno.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token

_ADMIN_ID = str(uuid.uuid4())
_GERENTE_ID = str(uuid.uuid4())
_LIDER_ID = str(uuid.uuid4())
_PROYECTO_ID = str(uuid.uuid4())
_AREA_ID = str(uuid.uuid4())

_GERENTE = {"id": _GERENTE_ID, "rol": "gerente"}
_LIDER = {"id": _LIDER_ID, "rol": "lider"}

_AREA = {
    "id": _AREA_ID,
    "proyecto_id": _PROYECTO_ID,
    "nombre": "Estructura",
    "cap_wbs": "1.2",
    "color": "#3B82F6",
    "responsable_nombre": None,
    "responsable_telefono": None,
    "responsable_email": None,
    "disponibilidad_horas": None,
    "cantidad_empleados": None,
    "gerente_id": None,
    "creado_en": datetime.utcnow().isoformat(),
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


def _admin_headers() -> dict:
    token = create_access_token(_ADMIN_ID, "administrador")
    return {"Authorization": f"Bearer {token}"}


async def test_asignar_dueno_gerente_valido_success(client):
    """(a) Asignar un gerente válido a un área → 200 con gerente_id en la respuesta."""
    actualizada = {**_AREA, "gerente_id": _GERENTE_ID}
    with patch("services.planificacion_service.planificacion_area_repo.find_by_id",
               return_value=_AREA), \
         patch("services.planificacion_service.user_repo.find_by_id", return_value=_GERENTE), \
         patch("services.planificacion_service.planificacion_area_repo.update",
               return_value=actualizada):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/areas/{_AREA_ID}/dueno",
            headers=_admin_headers(),
            json={"gerente_id": _GERENTE_ID},
        )
    assert resp.status_code == 200
    assert resp.json()["gerente_id"] == _GERENTE_ID


async def test_asignar_dueno_no_gerente_conflict(client):
    """(b) gerente_id de un usuario no-gerente → 409."""
    with patch("services.planificacion_service.planificacion_area_repo.find_by_id",
               return_value=_AREA), \
         patch("services.planificacion_service.user_repo.find_by_id", return_value=_LIDER):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/areas/{_AREA_ID}/dueno",
            headers=_admin_headers(),
            json={"gerente_id": _LIDER_ID},
        )
    assert resp.status_code == 409
    assert resp.json()["code"] == "VALIDATION_ERROR"


async def test_asignar_dueno_area_inexistente_not_found(client):
    """(c) Área inexistente → 404."""
    with patch("services.planificacion_service.planificacion_area_repo.find_by_id",
               return_value=None):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/areas/{_AREA_ID}/dueno",
            headers=_admin_headers(),
            json={"gerente_id": _GERENTE_ID},
        )
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


async def test_asignar_dueno_area_de_otro_proyecto_not_found(client):
    """(d) Área que pertenece a otro proyecto → 404."""
    otro_proyecto = str(uuid.uuid4())
    with patch("services.planificacion_service.planificacion_area_repo.find_by_id",
               return_value=_AREA):
        resp = await client.patch(
            f"/api/v1/planificacion/{otro_proyecto}/areas/{_AREA_ID}/dueno",
            headers=_admin_headers(),
            json={"gerente_id": _GERENTE_ID},
        )
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


async def test_desasignar_dueno_null_success(client):
    """(e) Desasignar con gerente_id null → 200 (no valida rol)."""
    actualizada = {**_AREA, "gerente_id": None}
    with patch("services.planificacion_service.planificacion_area_repo.find_by_id",
               return_value=_AREA), \
         patch("services.planificacion_service.planificacion_area_repo.update",
               return_value=actualizada) as mock_update, \
         patch("services.planificacion_service.user_repo.find_by_id") as mock_user:
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/areas/{_AREA_ID}/dueno",
            headers=_admin_headers(),
            json={"gerente_id": None},
        )
    assert resp.status_code == 200
    assert resp.json()["gerente_id"] is None
    mock_user.assert_not_called()
    mock_update.assert_called_once_with(_AREA_ID, {"gerente_id": None})


async def test_asignar_dueno_como_no_admin_forbidden(client):
    """(f) Un rol no-admin (gerente) → 403."""
    token = create_access_token(_GERENTE_ID, "gerente")
    resp = await client.patch(
        f"/api/v1/planificacion/{_PROYECTO_ID}/areas/{_AREA_ID}/dueno",
        headers={"Authorization": f"Bearer {token}"},
        json={"gerente_id": _GERENTE_ID},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"
