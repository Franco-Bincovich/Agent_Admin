from __future__ import annotations

from pathlib import Path

from integrations.supabase_client import get_supabase
from utils.errors import AppError

_BUCKET = "cronogramas"

_CONTENT_TYPES = {
    ".xml": "application/xml",
}


def upload_cronograma(proyecto_id: str, filename: str, file_bytes: bytes) -> str:
    """
    Sube el archivo de cronograma al bucket 'cronogramas' de Supabase Storage
    y retorna la URL pública.

    El path en el bucket se construye como {proyecto_id}{ext}, donde ext es la
    extensión del filename original (.xml o .mpp).
    content-type: 'application/xml' para .xml, 'application/octet-stream' para el resto.

    Args:
        proyecto_id: UUID del proyecto. Usado como nombre base del archivo en el bucket.
        filename: Nombre original del archivo. Solo se usa para derivar la extensión.
        file_bytes: Contenido binario del archivo.

    Returns:
        URL pública del archivo en Supabase Storage.

    Raises:
        AppError: STORAGE_ERROR/502 si el upload falla.
    """
    try:
        ext = Path(filename).suffix.lower()
        path = f"{proyecto_id}{ext}"
        content_type = _CONTENT_TYPES.get(ext, "application/octet-stream")
        storage = get_supabase().storage.from_(_BUCKET)
        storage.upload(path=path, file=file_bytes, file_options={"content-type": content_type})
        return storage.get_public_url(path)
    except Exception as exc:
        raise AppError(
            f"Error al subir cronograma a Storage: {exc}", "STORAGE_ERROR", 502
        ) from exc
