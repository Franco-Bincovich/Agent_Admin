from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from integrations.supabase_client import get_supabase

_TABLE = "video_jobs"


def _db():
    return get_supabase().table(_TABLE)


async def create(
    usuario_id: str,
    titulo: str,
    video_input_url: str,
    parametros: dict,
) -> dict:
    """
    Inserta un video job con estado='pending' y retorna el registro completo.

    Args:
        usuario_id: UUID del usuario propietario del job.
        titulo: Título descriptivo del job.
        video_input_url: URL del video fuente en Storage.
        parametros: JSONB con las variantes de edición y cualquier config adicional.

    Returns:
        Dict con todos los campos del registro recién insertado.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .insert({
            "usuario_id": str(usuario_id),
            "titulo": titulo,
            "video_input_url": video_input_url,
            "parametros": parametros,
            "estado": "pending",
        })
        .execute()
    )
    return response.data[0]


async def find_by_id(job_id: str) -> dict | None:
    """
    Retorna el video job por ID, o None si no existe.

    Args:
        job_id: UUID del job a buscar.

    Returns:
        Dict con el registro, o None si no se encuentra.
    """
    response = await asyncio.to_thread(
        lambda: _db().select("*").eq("id", str(job_id)).execute()
    )
    return response.data[0] if response.data else None


async def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """
    Retorna los video jobs del usuario ordenados por creado_en DESC.

    Args:
        usuario_id: UUID del usuario propietario.
        limit: Máximo de registros a retornar (default 20).

    Returns:
        Lista de dicts ordenada por fecha de creación descendente.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("usuario_id", str(usuario_id))
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


async def update_estado(
    job_id: str,
    estado: str,
    output_url: str | None = None,
    error_message: str | None = None,
) -> None:
    """
    Actualiza el estado del video job y registra el timestamp de actualización.

    Campos opcionales incluidos solo cuando se proveen:
    - output_url: URL del video procesado (cuando estado='completed').
    - error_message: Descripción del error (cuando estado='failed').

    Args:
        job_id: UUID del job a actualizar.
        estado: Nuevo estado. Valores válidos: 'pending', 'processing', 'completed', 'failed'.
        output_url: URL del video resultado en Storage. None si no aplica.
        error_message: Mensaje de error del pipeline. None si no aplica.
    """
    payload: dict = {"estado": estado, "actualizado_en": datetime.now(timezone.utc).isoformat()}
    if output_url is not None:
        payload["output_url"] = output_url
    if error_message is not None:
        payload["error_message"] = error_message
    await asyncio.to_thread(
        lambda: _db().update(payload).eq("id", str(job_id)).execute()
    )
