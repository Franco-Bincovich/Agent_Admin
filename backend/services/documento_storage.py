from __future__ import annotations

from urllib.parse import unquote, urlparse

import httpx

from config.settings import get_settings
from integrations.supabase_client import get_supabase
from utils.errors import AppError
from utils.logger import log

_DOCX_BUCKET = "docx-generados"


def _validate_storage_url(url: str) -> None:
    """
    Verifica que la URL pertenezca al Storage de Supabase configurado.
    Previene SSRF rechazando URLs que apunten a otros hosts.

    Raises:
        AppError URL_NOT_ALLOWED (400) si el host no coincide.
    """
    parsed_url = urlparse(url)
    parsed_supabase = urlparse(get_settings().supabase_url)
    if parsed_url.netloc != parsed_supabase.netloc:
        raise AppError(
            "URL no permitida",
            "URL_NOT_ALLOWED",
            400,
        )


async def _download_file(url: str) -> tuple[str, bytes]:
    """
    Descarga un archivo desde una URL de Supabase Storage.

    Args:
        url: URL pública (o firmada) del archivo a descargar.

    Returns:
        Tupla (nombre_archivo, bytes). El nombre se deriva del último
        segmento del path de la URL.

    Raises:
        AppError DOWNLOAD_FAILED (502) si la descarga falla.
    """
    try:
        _validate_storage_url(url)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AppError(
            f"No se pudo descargar el archivo desde Storage: {exc}",
            "DOWNLOAD_FAILED",
            502,
        ) from exc
    nombre = unquote(urlparse(url).path.rsplit("/", 1)[-1]) or "archivo"
    return nombre, response.content


def _upload_docx(documento_id: str, docx_bytes: bytes) -> str:
    """
    Sube los bytes del DOCX al bucket de Supabase Storage y retorna la URL pública.

    Args:
        documento_id: UUID usado como nombre de archivo ({documento_id}.docx).
        docx_bytes: Contenido binario del archivo DOCX.

    Returns:
        URL pública del archivo en Supabase Storage.
    """
    path = f"{documento_id}.docx"
    storage = get_supabase().storage.from_(_DOCX_BUCKET)
    storage.upload(
        path=path,
        file=docx_bytes,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        },
    )
    return storage.get_public_url(path)
