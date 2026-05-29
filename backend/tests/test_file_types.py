"""
Tests de tipos de archivo aceptados/rechazados en POST /api/v1/generations/.
Cubre extensiones soportadas, no soportadas, archivos vacíos y nombres especiales.
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

_BASE_DATA = {
    "objetivo": "Presentar resultados Q1 a directivos",
    "template": "ejecutivo_oscuro",
    "tono": "formal",
    "audiencia": "directivos",
    "output": "pptx",
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac


def _accept_mocks():
    """Helper: agrupa los patches necesarios para que el pipeline acepte un archivo."""
    return [
        patch("services.generation_record_service.extract_text_from_file",
              return_value="Texto de prueba con contenido suficiente para validar el pipeline completo."),
        patch("services.generation_record_service.find_user_by_id", return_value=_USER),
        patch("services.generation_record_service.generation_repo.create",
              return_value=_FAKE_GEN_PROCESANDO),
        patch("services.generation_service.generate_outline", new_callable=AsyncMock, return_value=_FAKE_OUTLINE),
        patch("services.generation_service.generate_pptx", return_value=b"fake-pptx"),
        patch("services.generation_service.generation_repo.update_resultado"),
        patch("services.generation_service.generation_repo.update_error"),
    ]


async def _post_with_file(client, filename: str, content: bytes = b"contenido valido", mime: str = "application/octet-stream"):
    token = create_access_token(_USER_ID, "editor")
    return await client.post(
        "/api/v1/generations/",
        headers={"Authorization": f"Bearer {token}"},
        files={"archivos": (filename, content, mime)},
        data=_BASE_DATA,
    )


# ── Archivos aceptados ──────────────────────────────────────────────────────


async def test_accept_txt_file(client):
    """Archivo .txt debe aceptarse y retornar 202."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(client, "informe.txt", b"texto plano", "text/plain")
    assert resp.status_code == 202


async def test_accept_pdf_file(client):
    """Archivo .pdf debe aceptarse y retornar 202."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(client, "informe.pdf", b"%PDF-1.4 fake", "application/pdf")
    assert resp.status_code == 202


async def test_accept_docx_file(client):
    """Archivo .docx debe aceptarse y retornar 202."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(client, "informe.docx", b"PK fake docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert resp.status_code == 202


async def test_accept_pptx_file(client):
    """Archivo .pptx debe aceptarse y retornar 202 (con mock del extractor PPTX)."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(client, "deck.pptx", b"PK fake pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    assert resp.status_code == 202


async def test_accept_xlsx_file(client):
    """Archivo .xlsx debe aceptarse y retornar 202."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(client, "datos.xlsx", b"PK fake xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    assert resp.status_code == 202


# ── Imágenes como archivo principal: rechazadas — el sistema sólo extrae texto ──


async def test_reject_png_as_archivo(client):
    """Imagen .png como archivo principal debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "foto.png", b"\x89PNG fake", "image/png")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "UNSUPPORTED_FORMAT"


async def test_reject_jpg_as_archivo(client):
    """Imagen .jpg como archivo principal debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "foto.jpg", b"\xff\xd8 fake jpg", "image/jpeg")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "UNSUPPORTED_FORMAT"


# ── Extensiones explícitamente rechazadas ────────────────────────────────────


async def test_reject_exe_file(client):
    """Archivo .exe debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "malware.exe", b"MZ fake")
    assert resp.status_code == 400
    assert resp.json()["code"] == "UNSUPPORTED_FORMAT"


async def test_reject_zip_file(client):
    """Archivo .zip debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "paquete.zip", b"PK fake zip")
    assert resp.status_code == 400
    assert resp.json()["code"] == "UNSUPPORTED_FORMAT"


async def test_reject_js_file(client):
    """Archivo .js debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "script.js", b"console.log('x')")
    assert resp.status_code == 400
    assert resp.json()["code"] == "UNSUPPORTED_FORMAT"


async def test_reject_py_file(client):
    """Archivo .py debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "script.py", b"print('x')")
    assert resp.status_code == 400
    assert resp.json()["code"] == "UNSUPPORTED_FORMAT"


# ── Casos borde de validación de archivo ────────────────────────────────────


async def test_reject_empty_file(client):
    """Archivo de 0 bytes debe rechazarse con EMPTY_FILE (< 50 chars de texto)."""
    resp = await _post_with_file(client, "vacio.txt", b"", "text/plain")
    assert resp.status_code in (400, 422)
    body = resp.json()
    assert body["error"] is True
    assert body["code"] in ("EMPTY_FILE", "UNSUPPORTED_FORMAT")


async def test_reject_file_without_extension(client):
    """Archivo sin extensión debe rechazarse con UNSUPPORTED_FORMAT."""
    resp = await _post_with_file(client, "informe", b"contenido sin extension")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "UNSUPPORTED_FORMAT"


async def test_accept_multiple_files_in_request(client):
    """Múltiples archivos en un mismo request deben aceptarse."""
    token = create_access_token(_USER_ID, "editor")
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await client.post(
            "/api/v1/generations/",
            headers={"Authorization": f"Bearer {token}"},
            files=[
                ("archivos", ("a.txt", b"contenido a", "text/plain")),
                ("archivos", ("b.txt", b"contenido b", "text/plain")),
            ],
            data=_BASE_DATA,
        )
    assert resp.status_code == 202


async def test_accept_filename_with_special_chars(client):
    """Archivo con caracteres especiales en el nombre debe aceptarse limpiamente (sin 500)."""
    mocks = _accept_mocks()
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6], \
         patch("services.generation_storage.get_supabase") as mock_supabase:
        mock_supabase.return_value.storage.from_.return_value.get_public_url.return_value = _PPTX_URL
        resp = await _post_with_file(
            client, "informe ñoño & cía (2024).txt", b"texto", "text/plain",
        )
    assert resp.status_code != 500
    assert resp.status_code in (200, 202)
