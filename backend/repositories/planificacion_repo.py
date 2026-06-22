from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from integrations.supabase_client import get_supabase

_TABLE = "planificacion_proyectos"


def _db():
    return get_supabase().table(_TABLE)


async def create(
    usuario_id: str,
    nombre: str,
    expediente: str | None,
    prioridad: str,
) -> dict:
    """Inserta proyecto con estado='procesando' y retorna el registro completo."""
    response = await asyncio.to_thread(
        lambda: _db()
        .insert({
            "usuario_id": str(usuario_id),
            "nombre": nombre,
            "expediente": expediente,
            "prioridad": prioridad,
            "estado": "procesando",
        })
        .execute()
    )
    return response.data[0]


async def update_resultado(
    proyecto_id: str,
    origen: str,
    archivo_url: str | None,
    fecha_inicio: str | None,
    fecha_fin: str | None,
) -> dict:
    """Actualiza a estado='listo' y persiste origen, archivo_url y fechas derivadas del cronograma."""
    response = await asyncio.to_thread(
        lambda: _db()
        .update({
            "estado": "listo",
            "origen": origen,
            "archivo_url": archivo_url,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        })
        .eq("id", str(proyecto_id))
        .execute()
    )
    return response.data[0]


async def update_error(proyecto_id: str, error_detalle: str | None = None) -> None:
    """Actualiza el proyecto a estado='error' y persiste el detalle del fallo."""
    await asyncio.to_thread(
        lambda: _db()
        .update({"estado": "error", "error_detalle": error_detalle})
        .eq("id", str(proyecto_id))
        .execute()
    )


async def find_by_id(proyecto_id: str) -> dict | None:
    """Retorna el proyecto por ID, o None si no existe."""
    response = await asyncio.to_thread(
        lambda: _db().select("*").eq("id", str(proyecto_id)).execute()
    )
    return response.data[0] if response.data else None


async def find_all(limit: int = 50) -> list[dict]:
    """Retorna todos los proyectos ordenados por creado_en DESC (lectura compartida)."""
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


async def delete_by_id(proyecto_id: str) -> None:
    """Elimina el proyecto. Áreas y tareas se borran en cascada (ON DELETE CASCADE)."""
    await asyncio.to_thread(
        lambda: _db().delete().eq("id", str(proyecto_id)).execute()
    )


async def find_stalled(older_than_minutes: int = 30) -> dict:
    """
    Devuelve proyectos en estado 'procesando' con más de
    older_than_minutes minutos sin actualización. Usado por el reaper de main.py.
    """
    cutoff = (
        datetime.now(timezone.utc) - timedelta(minutes=older_than_minutes)
    ).isoformat()
    return await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("estado", "procesando")
        .lt("creado_en", cutoff)
        .execute()
    )
