"""
Tests de generación — pipeline PPTX, archivo inválido, ownership.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

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

_GEN_ID        = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())

_FAKE_OUTLINE = {
    "slides": [
        {"tipo": "portada",   "titulo": "Resultados Q1",  "contenido": "Resumen ejecutivo"},
        {"tipo": "contenido", "titulo": "Métricas clave", "contenido": "KPIs del trimestre"},
        {"tipo": "contenido", "titulo": "Avances",        "contenido": "Logros del período"},
        {"tipo": "contenido", "titulo": "Desafíos",       "contenido": "Obstáculos encontrados"},
        {"tipo": "cierre",    "titulo": "Conclusiones",   "contenido": "Próximos pasos"},
    ]
}

_PPTX_URL = "https://test.supabase.co/storage/v1/object/public/pptx-generados/test.pptx"

_FAKE_GEN_PROCESANDO = {
    "id": _GEN_ID,
    "usuario_id": _USER_ID,
    "objetivo": "Presentar resultados Q1 a directivos",
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


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── 8. Crear generación sin autenticación ───────────────────────────────────


async def test_create_generation_unauthorized(client):
    resp = await client.post("/api/v1/generations/")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


# ── 9. Generación PPTX exitosa ───────────────────────────────────────────────


async def test_generation_pptx_success(client):
    token = create_access_token(_USER_ID, "editor")

    with patch("controllers.generation_controller.extract_text_from_file",
               return_value="Texto de prueba con contenido suficiente para la validación del pipeline."), \
         patch("services.generation_record_service.generation_repo.create",
               return_value=_FAKE_GEN_PROCESANDO), \
         patch("services.generation_service.generate_outline", return_value=_FAKE_OUTLINE), \
         patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"), \
         patch("services.generation_service.get_supabase") as mock_supabase, \
         patch("services.generation_service.generation_repo.update_resultado") as mock_update, \
         patch("services.generation_service.generation_repo.update_error"):

        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL

        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files={"archivos": ("informe.txt", b"contenido de prueba para presentacion", "text/plain")},
            data={
                "objetivo": "Presentar resultados Q1 a directivos",
                "template": "ejecutivo_oscuro",
                "tono": "formal",
                "audiencia": "directivos",
                "output": "pptx",
            },
        )

    assert resp.status_code == 202
    mock_update.assert_called_once()
    assert mock_update.call_args.args[1] is not None
    assert mock_update.call_args.args[1] == _PPTX_URL


# ── 10. Archivo con extensión no soportada → 400 ────────────────────────────


async def test_generation_pptx_invalid_file(client):
    token = create_access_token(_USER_ID, "editor")
    resp = await client.post(
        "/api/v1/generations/",
        headers={"Authorization": f"Bearer {token}"},
        files={"archivos": ("malware.exe", b"MZ fake binary content", "application/octet-stream")},
        data={
            "objetivo": "Presentar resultados Q1 a directivos",
            "template": "ejecutivo_oscuro",
            "tono": "formal",
            "audiencia": "directivos",
            "output": "pptx",
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "UNSUPPORTED_FORMAT"


# ── 11. Owner descarga su propia generación ──────────────────────────────────


async def test_download_output_as_owner(client):
    token = create_access_token(_USER_ID, "editor")
    with patch("services.generation_record_service.generation_repo.find_by_id",
               return_value=_FAKE_GEN_LISTO):
        resp = await client.get(
            f"/api/v1/generations/{_GEN_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pptx_url"] == _PPTX_URL


# ── 12. Otro usuario obtiene 404 — nunca 403 ────────────────────────────────


async def test_download_output_as_other_user(client):
    other_token = create_access_token(_OTHER_USER_ID, "editor")
    with patch("services.generation_record_service.generation_repo.find_by_id",
               return_value=_FAKE_GEN_LISTO):
        resp = await client.get(
            f"/api/v1/generations/{_GEN_ID}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"] is True
