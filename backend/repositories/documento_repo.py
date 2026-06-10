from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from integrations.supabase_client import get_supabase, recreate_supabase_client

_TABLE = "documentos"


def _db():
    return get_supabase().table(_TABLE)


async def find_by_id(documento_id: str) -> dict | None:
    """Retorna el documento por ID, o None si no existe."""
    for attempt in range(2):
        try:
            response = await asyncio.to_thread(
                lambda: _db().select("*").eq("id", str(documento_id)).execute()
            )
            return response.data[0] if response.data else None
        except httpx.RemoteProtocolError:
            if attempt == 0:
                recreate_supabase_client()
                continue
            raise
    return None


async def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """Retorna los documentos del usuario ordenados por creado_en DESC."""
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
    """Retorna todos los documentos del sistema ordenados por creado_en DESC. Solo para administradores."""
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
    Devuelve documentos en estado 'procesando' con más de
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
