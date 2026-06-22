"""
Tests del Modelo A de permisos de escritura sobre tareas de Planificación.

Cubre la matriz de autorización resuelta por
services/planificacion_permisos.assert_puede_mutar_tarea, ejercida a través del
endpoint de actualizar progreso (PATCH .../tareas/{id}/progreso) y reprogramar,
más el endpoint de asignar-área-a-tarea que pasó a admin-only.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token

_ADMIN_ID = str(uuid.uuid4())
_GERENTE_DUENO_ID = str(uuid.uuid4())
_GERENTE_AJENO_ID = str(uuid.uuid4())
_LIDER_DEL_DUENO_ID = str(uuid.uuid4())
_LIDER_AJENO_ID = str(uuid.uuid4())
_PROYECTO_ID = str(uuid.uuid4())
_AREA_ID = str(uuid.uuid4())
_TAREA_ID = str(uuid.uuid4())

# Tarea base con todos los campos requeridos por TareaResponse.
_TAREA = {
    "id": _TAREA_ID,
    "proyecto_id": _PROYECTO_ID,
    "area_id": _AREA_ID,
    "wbs": "1.2.3",
    "nombre": "Hormigonado",
    "nivel": 3,
    "es_resumen": False,
    "fecha_inicio": "2026-01-10",
    "fecha_fin": "2026-01-20",
    "fecha_inicio_original": None,
    "fecha_fin_original": None,
    "fecha_estimada": False,
    "confianza": "alta",
    "predecesoras": None,
    "completada": False,
    "completada_en": None,
    "completada_por": None,
    "progreso": 0,
    "reprogramada": False,
    "creado_en": datetime.utcnow().isoformat(),
}

# Área cuyo dueño es _GERENTE_DUENO_ID.
_AREA_CON_DUENO = {"id": _AREA_ID, "gerente_id": _GERENTE_DUENO_ID}
_AREA_SIN_DUENO = {"id": _AREA_ID, "gerente_id": None}

_LIDER_DEL_DUENO = {"id": _LIDER_DEL_DUENO_ID, "rol": "lider", "manager_id": _GERENTE_DUENO_ID}
_LIDER_AJENO = {"id": _LIDER_AJENO_ID, "rol": "lider", "manager_id": _GERENTE_AJENO_ID}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


def _headers(user_id: str, role: str) -> dict:
    token = create_access_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


def _tarea_con(area_id: str | None) -> dict:
    return {**_TAREA, "area_id": area_id}


async def _patch_progreso(client, headers, *, tarea, area=None, usuario=None):
    """Ejecuta PATCH .../progreso con los repos mockeados según el escenario."""
    actualizada = {**tarea, "progreso": 50}
    with patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.find_by_id_and_proyecto",
        return_value=tarea,
    ), patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.actualizar_avance",
        return_value=actualizada,
    ), patch(
        "services.planificacion_permisos.planificacion_area_repo.find_by_id",
        return_value=area,
    ), patch(
        "services.planificacion_permisos.user_repo.find_by_id",
        return_value=usuario,
    ):
        return await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/progreso",
            headers=headers,
            json={"progreso": 50},
        )


# ── Matriz de permisos sobre mutación de avance (área con dueño) ───────────────

async def test_admin_puede_cualquier_tarea(client):
    """Admin → 200 sobre un área cuyo dueño es otro (no consulta área ni usuario)."""
    resp = await _patch_progreso(
        client, _headers(_ADMIN_ID, "administrador"), tarea=_TAREA, area=_AREA_CON_DUENO
    )
    assert resp.status_code == 200
    assert resp.json()["progreso"] == 50


async def test_gerente_dueno_puede(client):
    """Gerente dueño del área → 200."""
    resp = await _patch_progreso(
        client, _headers(_GERENTE_DUENO_ID, "gerente"), tarea=_TAREA, area=_AREA_CON_DUENO
    )
    assert resp.status_code == 200


async def test_gerente_no_dueno_forbidden(client):
    """Gerente que NO es dueño del área → 403."""
    resp = await _patch_progreso(
        client, _headers(_GERENTE_AJENO_ID, "gerente"), tarea=_TAREA, area=_AREA_CON_DUENO
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


async def test_lider_del_dueno_puede(client):
    """Líder cuyo manager_id es el gerente dueño → 200."""
    resp = await _patch_progreso(
        client,
        _headers(_LIDER_DEL_DUENO_ID, "lider"),
        tarea=_TAREA,
        area=_AREA_CON_DUENO,
        usuario=_LIDER_DEL_DUENO,
    )
    assert resp.status_code == 200


async def test_lider_ajeno_forbidden(client):
    """Líder cuyo manager NO es el dueño → 403."""
    resp = await _patch_progreso(
        client,
        _headers(_LIDER_AJENO_ID, "lider"),
        tarea=_TAREA,
        area=_AREA_CON_DUENO,
        usuario=_LIDER_AJENO,
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


# ── Estados abiertos (transitorios) ────────────────────────────────────────────

async def test_area_sin_dueno_cualquiera_puede(client):
    """Área sin dueño (gerente_id None) → cualquier autenticado puede (200)."""
    resp = await _patch_progreso(
        client,
        _headers(_LIDER_AJENO_ID, "lider"),
        tarea=_TAREA,
        area=_AREA_SIN_DUENO,
    )
    assert resp.status_code == 200


async def test_tarea_sin_area_cualquiera_puede(client):
    """Tarea sin área (area_id None) → abierto; el área no se consulta."""
    tarea = _tarea_con(None)
    with patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.find_by_id_and_proyecto",
        return_value=tarea,
    ), patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.actualizar_avance",
        return_value={**tarea, "progreso": 50},
    ), patch(
        "services.planificacion_permisos.planificacion_area_repo.find_by_id",
    ) as mock_area:
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/progreso",
            headers=_headers(_LIDER_AJENO_ID, "lider"),
            json={"progreso": 50},
        )
    assert resp.status_code == 200
    mock_area.assert_not_called()


# ── Reprogramar: confirma el nuevo parámetro current_user en su firma ──────────

async def test_reprogramar_aplica_modelo_a(client):
    """Reprogramar respeta el Modelo A: líder ajeno sobre área con dueño → 403."""
    with patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.find_by_id_and_proyecto",
        return_value=_TAREA,
    ), patch(
        "services.planificacion_permisos.planificacion_area_repo.find_by_id",
        return_value=_AREA_CON_DUENO,
    ), patch(
        "services.planificacion_permisos.user_repo.find_by_id",
        return_value=_LIDER_AJENO,
    ):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/reprogramar",
            headers=_headers(_LIDER_AJENO_ID, "lider"),
            json={"fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-15"},
        )
    assert resp.status_code == 403


async def test_reprogramar_dueno_ok(client):
    """Reprogramar como gerente dueño → 200 y estampa la reprogramación."""
    actualizada = {**_TAREA, "reprogramada": True, "fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-15"}
    with patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.find_by_id_and_proyecto",
        return_value=_TAREA,
    ), patch(
        "services.planificacion_tarea_service.planificacion_tarea_repo.reprogramar_tarea",
        return_value=actualizada,
    ), patch(
        "services.planificacion_permisos.planificacion_area_repo.find_by_id",
        return_value=_AREA_CON_DUENO,
    ):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/reprogramar",
            headers=_headers(_GERENTE_DUENO_ID, "gerente"),
            json={"fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-15"},
        )
    assert resp.status_code == 200
    assert resp.json()["reprogramada"] is True


# ── Asignar área a tarea: admin-only ───────────────────────────────────────────

async def test_asignar_area_a_tarea_no_admin_forbidden(client):
    """Asignar área a una tarea como no-admin (gerente) → 403, sin tocar repos."""
    resp = await client.patch(
        f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/area",
        headers=_headers(_GERENTE_DUENO_ID, "gerente"),
        json={"area_id": _AREA_ID},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


async def test_asignar_area_a_tarea_admin_ok(client):
    """Asignar área a una tarea como admin → 200."""
    actualizada = {**_TAREA, "area_id": _AREA_ID}
    with patch(
        "controllers.planificacion_controller.planificacion_tarea_repo.find_by_id_and_proyecto",
        return_value=_TAREA,
    ), patch(
        "controllers.planificacion_controller.planificacion_tarea_repo.update_area",
        return_value=actualizada,
    ):
        resp = await client.patch(
            f"/api/v1/planificacion/{_PROYECTO_ID}/tareas/{_TAREA_ID}/area",
            headers=_headers(_ADMIN_ID, "administrador"),
            json={"area_id": _AREA_ID},
        )
    assert resp.status_code == 200
