"""
Tests básicos del módulo de video (en desarrollo).

Marcados con @pytest.mark.video — para correr sólo video: pytest -m video
Para excluir video: pytest --ignore=backend/tests/test_video_basic.py
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token, hash_password

pytestmark = pytest.mark.video

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())
_JOB_ID = str(uuid.uuid4())

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": "test@example.com",
    "password_hash": hash_password(_PASSWORD),
    "rol": "editor",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}

_FAKE_JOB = {
    "id": _JOB_ID,
    "usuario_id": _USER_ID,
    "titulo": "Mi video",
    "estado": "pending",
    "video_input_url": "https://test.supabase.co/videos-input/foo.mp4",
    "output_url": None,
    "parametros": {},
    "error_message": None,
    "creado_en": datetime.utcnow().isoformat(),
}

_VARIANTE_VALIDA = (
    '[{"estilo": "dinamico", "formato": "horizontal_16_9", '
    '"posicion_subtitulos": "abajo", "resolucion": "hd_720p"}]'
)


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_list_video_jobs_without_token(client):
    """GET /video/jobs sin token devuelve 401."""
    resp = await client.get("/api/v1/video/jobs")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


async def test_create_video_job_without_token(client):
    """POST /video/jobs sin token devuelve 401."""
    resp = await client.post("/api/v1/video/jobs")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


async def test_create_video_job_minimal_payload(client):
    """POST /video/jobs con token y payload mínimo válido devuelve 202."""
    token = create_access_token(_USER_ID, "editor")
    with patch("controllers.video_controller.get_supabase") as mock_supabase, \
         patch("controllers.video_controller.create_video_job", return_value=_FAKE_JOB), \
         patch("controllers.video_controller.run_video_job"):
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = \
            "https://test.supabase.co/videos-input/foo.mp4"
        resp = await client.post(
            "/api/v1/video/jobs",
            headers={"Authorization": f"Bearer {token}"},
            files={"video": ("clip.mp4", b"fake video bytes", "video/mp4")},
            data={"titulo": "Mi video", "variantes": _VARIANTE_VALIDA},
        )
    assert resp.status_code == 202
    body = resp.json()
    assert body["id"] == _JOB_ID


async def test_create_video_job_invalid_variantes(client):
    """POST /video/jobs con variantes inválidas devuelve 400 con VALIDATION_ERROR."""
    token = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/video/jobs",
        headers={"Authorization": f"Bearer {token}"},
        files={"video": ("clip.mp4", b"fake", "video/mp4")},
        data={"titulo": "Mi video", "variantes": "esto-no-es-json"},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "VALIDATION_ERROR"


async def test_get_video_job_of_other_user_returns_404(client):
    """GET /video/jobs/{id} de un job de otro usuario devuelve 404 (ownership)."""
    other_token = create_access_token(_OTHER_USER_ID, "editor")
    with patch("services.video.video_record_service.video_repo.find_by_id",
               return_value=_FAKE_JOB):
        resp = await client.get(
            f"/api/v1/video/jobs/{_JOB_ID}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "NOT_FOUND"


@pytest.mark.skip(reason="El endpoint actual no valida extensión del video — pendiente fase 2")
async def test_create_video_job_unsupported_format(client):
    """POST /video/jobs con archivo no-video debería rechazarse con UNSUPPORTED_FORMAT."""
    token = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/video/jobs",
        headers={"Authorization": f"Bearer {token}"},
        files={"video": ("malware.exe", b"MZ", "application/octet-stream")},
        data={"titulo": "x", "variantes": _VARIANTE_VALIDA},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "UNSUPPORTED_FORMAT"
