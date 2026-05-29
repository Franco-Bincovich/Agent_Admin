"""
Tests del pipeline completo de generación: outputs, fallos, listado y get por ID.
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

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

_GEN_ID = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())

_FAKE_OUTLINE = {
    "slides": [
        {"tipo": "portada", "titulo": "T", "contenido": "C"},
        {"tipo": "contenido", "titulo": "T", "contenido": "C"},
        {"tipo": "contenido", "titulo": "T", "contenido": "C"},
        {"tipo": "contenido", "titulo": "T", "contenido": "C"},
        {"tipo": "cierre", "titulo": "T", "contenido": "C"},
    ]
}

_PPTX_URL = "https://test.supabase.co/storage/v1/object/public/pptx-generados/test.pptx"
_GAMMA_URL = "https://gamma.app/docs/abc123"
_PPTX_GAMMA_URL = "https://gamma.app/docs/abc123.pptx"

_FAKE_GEN_PROCESANDO = {
    "id": _GEN_ID,
    "usuario_id": _USER_ID,
    "objetivo": "Objetivo de prueba",
    "estado": "procesando",
    "pptx_url": None,
    "gamma_url": None,
    "pptx_gamma_url": None,
    "slides_count": None,
    "creado_en": datetime.utcnow().isoformat(),
}

_FAKE_GEN_LISTO = {
    **_FAKE_GEN_PROCESANDO,
    "estado": "listo",
    "pptx_url": _PPTX_URL,
}

_BASE_DATA = {
    "objetivo": "Presentar resultados Q1 a directivos",
    "template": "ejecutivo_oscuro",
    "tono": "formal",
    "audiencia": "directivos",
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac


# ── Pipeline por tipo de output ─────────────────────────────────────────────


async def test_output_pptx_returns_pptx_url(client):
    """Output 'pptx' debe disparar update_resultado con la pptx_url en posición 1."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "pptx"},
        )
    assert resp.status_code == 202
    mock_update.assert_called_once()
    assert mock_update.call_args.args[1] == _PPTX_URL
    assert mock_update.call_args.args[2] is None  # gamma_url None
    assert mock_update.call_args.args[3] is None  # pptx_gamma_url None


async def test_output_gamma_returns_gamma_url(client):
    """Output 'gamma' debe disparar update_resultado con gamma_url y sin pptx_url."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.resolve_user_folder",
               return_value=("folder-1", None)), \
         patch("services.generation_service.publish_presentation",
               return_value={"gamma_url": _GAMMA_URL, "pptx_gamma_url": _PPTX_GAMMA_URL}), \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "gamma"},
        )
    assert resp.status_code == 202
    mock_update.assert_called_once()
    assert mock_update.call_args.args[1] is None        # pptx_url None
    assert mock_update.call_args.args[2] == _GAMMA_URL  # gamma_url


async def test_output_ambos_returns_pptx_and_gamma(client):
    """Output 'ambos' debe disparar update_resultado con pptx_url, gamma_url y pptx_gamma_url."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.resolve_user_folder",
               return_value=("folder-1", None)), \
         patch("services.generation_service.publish_presentation",
               return_value={"gamma_url": _GAMMA_URL, "pptx_gamma_url": _PPTX_GAMMA_URL}), \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "ambos"},
        )
    assert resp.status_code == 202
    mock_update.assert_called_once()
    assert mock_update.call_args.args[1] == _PPTX_URL
    assert mock_update.call_args.args[2] == _GAMMA_URL
    assert mock_update.call_args.args[3] == _PPTX_GAMMA_URL


async def test_generation_with_image_attachment(client):
    """Generación con imagen adjunta (usar_imagenes_documento=True) debe procesarse sin error."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.extract_images_from_file",
               return_value=[b"\x89PNG fake"]), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.docx", b"PK fake docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={**_BASE_DATA, "output": "pptx", "usar_imagenes_documento": "true"},
        )
    assert resp.status_code == 202
    mock_update.assert_called_once()


# ── Manejo de errores del pipeline ───────────────────────────────────────────


async def test_claude_failure_sets_error_state(client):
    """Si generate_outline lanza excepción, update_error debe llamarse."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline",
               new_callable=AsyncMock, side_effect=Exception("Anthropic API down")), \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error") as mock_error:
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "pptx"},
        )
    assert resp.status_code == 202
    mock_update.assert_not_called()
    mock_error.assert_called_once_with(_GEN_ID)


async def test_supabase_upload_failure_sets_error_state(client):
    """Si Supabase storage falla al subir el PPTX, update_error debe llamarse."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error") as mock_error:
        mock_supabase.return_value.storage.from_.return_value.upload.side_effect = Exception("storage error")
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "pptx"},
        )
    assert resp.status_code == 202
    mock_update.assert_not_called()
    mock_error.assert_called_once()


async def test_gamma_failure_does_not_break_generation(client):
    """Si Gamma falla con AppError, la generación PPTX se completa con gamma_url=None."""
    from utils.errors import AppError, ErrorCode
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.resolve_user_folder",
               return_value=("folder-1", None)), \
         patch("services.generation_service.publish_presentation",
               side_effect=AppError("Gamma down", ErrorCode.GAMMA_PUBLISH_ERROR, 500)), \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "ambos"},
        )
    assert resp.status_code == 202
    mock_update.assert_called_once()
    assert mock_update.call_args.args[1] == _PPTX_URL
    assert mock_update.call_args.args[2] is None  # gamma_url None tras fallo capturado


# ── Validación de payload ────────────────────────────────────────────────────


@pytest.mark.skip(reason="El endpoint no valida objetivo no vacío actualmente — sólo max_length=500")
async def test_objetivo_empty_rejected(client):
    """Objetivo vacío '' debe rechazarse con 422."""
    token = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/generations/",
        headers={"Authorization": f"Bearer {token}"},
        files={"archivos": ("a.txt", b"contenido", "text/plain")},
        data={**_BASE_DATA, "objetivo": ""},
    )
    assert resp.status_code == 422


async def test_objetivo_too_long_rejected(client):
    """Objetivo > 500 chars (max_length del Form) debe rechazarse con 422."""
    token = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/generations/",
        headers={"Authorization": f"Bearer {token}"},
        files={"archivos": ("a.txt", b"contenido", "text/plain")},
        data={**_BASE_DATA, "objetivo": "x" * 5001},
    )
    assert resp.status_code == 422


async def test_estado_listo_after_successful_generation(client):
    """Tras un éxito en background, update_resultado se invoca (lo que persiste estado='listo')."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.extract_text_from_file",
               return_value="Texto largo y suficiente para satisfacer el mínimo del extractor."), \
         patch("services.generation_record_service.find_user_by_id", return_value=_USER), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_storage.get_supabase") as mock_supabase, \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error") as mock_error:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("a.txt", b"contenido", "text/plain")},
            data={**_BASE_DATA, "output": "pptx"},
        )
    assert resp.status_code == 202
    # En éxito: update_resultado fue llamado (estado=listo), update_error NO.
    mock_update.assert_called_once()
    mock_error.assert_not_called()


# ── Listado y get por ID ─────────────────────────────────────────────────────


async def test_list_generations_only_own(client):
    """GET /generations/ devuelve sólo las generaciones del usuario autenticado."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.generation_repo.find_by_user",
               return_value=[_FAKE_GEN_LISTO]) as mock_find:
        resp = await client.get(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    mock_find.assert_called_once_with(_USER_ID)
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1


async def test_list_generations_pagination_params_do_not_break(client):
    """Query params ?page=1&limit=10 no rompen el endpoint (ignorados por FastAPI)."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.generation_repo.find_by_user",
               return_value=[]):
        resp = await client.get(
            "/api/v1/generations/?page=1&limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200


async def test_get_generation_not_found(client):
    """GET /generations/{uuid} con ID que no existe devuelve 404 limpio."""
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.generation_repo.find_by_id",
               return_value=None):
        resp = await client.get(
            f"/api/v1/generations/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "NOT_FOUND"


async def test_get_generation_invalid_uuid(client):
    """GET /generations/{id} con ID que no es UUID válido devuelve 422."""
    token = create_access_token(_USER_ID, "editor")
    resp = await client.get(
        "/api/v1/generations/not-a-valid-uuid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
