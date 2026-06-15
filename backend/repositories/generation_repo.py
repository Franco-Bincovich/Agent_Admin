from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from integrations.supabase_client import get_supabase
from utils.logger import log

_TABLE = "generaciones"


def _db():
    return get_supabase().table(_TABLE)


async def create(usuario_id: str, objetivo: str, archivos: list, parametros: dict, titulo: str = "") -> dict:
    """Inserta generación con estado='procesando' y retorna el registro completo."""
    response = await asyncio.to_thread(
        lambda: _db()
        .insert({
            "usuario_id": str(usuario_id),
            "titulo": titulo,
            "objetivo": objetivo,
            "archivos": archivos,
            "parametros": parametros,
            "estado": "procesando",
        })
        .execute()
    )
    return response.data[0]


async def update_resultado(
    generation_id: str,
    pptx_url: str | None,
    gamma_url: str | None,
    pptx_gamma_url: str | None,
    slides_count: int,
    outline: dict,
    gamma_warning: str | None = None,
    tabla_warning: str | None = None,
) -> dict:
    """Actualiza a estado='listo' y persiste urls, slides_count, outline, gamma_warning y tabla_warning."""
    response = await asyncio.to_thread(
        lambda: _db()
        .update({
            "estado": "listo",
            "pptx_url": pptx_url,
            "gamma_url": gamma_url,
            "pptx_gamma_url": pptx_gamma_url,
            "slides_count": slides_count,
            "outline": outline,
            "gamma_warning": gamma_warning,
            "tabla_warning": tabla_warning,
        })
        .eq("id", str(generation_id))
        .execute()
    )
    return response.data[0]


async def update_error(generation_id: str) -> None:
    """Actualiza la generación a estado='error'."""
    await asyncio.to_thread(
        lambda: _db().update({"estado": "error"}).eq("id", str(generation_id)).execute()
    )


async def find_by_id(generation_id: str) -> dict | None:
    """Retorna la generación por ID, o None si no existe."""
    response = await asyncio.to_thread(
        lambda: _db().select("*").eq("id", str(generation_id)).execute()
    )
    return response.data[0] if response.data else None


async def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """
    Retorna las generaciones del usuario ordenadas por creado_en DESC.
    Máximo `limit` registros (default 20).
    """
    log.info("find_by_user query", extra={"usuario_id": str(usuario_id)})
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("usuario_id", str(usuario_id))
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


async def find_all(limit: int = 50) -> list[dict]:
    """
    Retorna todas las generaciones del sistema ordenadas por creado_en DESC.
    Solo para administradores. Máximo `limit` registros (default 50).
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


async def find_stalled(older_than_minutes: int = 30) -> dict:
    """
    Devuelve generaciones en estado 'procesando' con más de
    older_than_minutes minutos sin actualización.
    """
    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(minutes=older_than_minutes)
    ).isoformat()
    return await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("estado", "procesando")
        .lt("creado_en", cutoff)
        .execute()
    )
