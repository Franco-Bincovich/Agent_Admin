from __future__ import annotations

import asyncio

from integrations.supabase_client import get_supabase

_TABLE = "planificacion_areas"


def _db():
    return get_supabase().table(_TABLE)


async def create(
    proyecto_id: str,
    nombre: str,
    cap_wbs: str | None = None,
    color: str | None = None,
    responsable_nombre: str | None = None,
    responsable_telefono: str | None = None,
    responsable_email: str | None = None,
    disponibilidad_horas: int | None = None,
    cantidad_empleados: int | None = None,
) -> dict:
    """Inserta un área y retorna el registro completo."""
    response = await asyncio.to_thread(
        lambda: _db()
        .insert({
            "proyecto_id": str(proyecto_id),
            "nombre": nombre,
            "cap_wbs": cap_wbs,
            "color": color,
            "responsable_nombre": responsable_nombre,
            "responsable_telefono": responsable_telefono,
            "responsable_email": responsable_email,
            "disponibilidad_horas": disponibilidad_horas,
            "cantidad_empleados": cantidad_empleados,
        })
        .execute()
    )
    return response.data[0]


async def find_by_proyecto(proyecto_id: str) -> list[dict]:
    """Retorna todas las áreas de un proyecto ordenadas por creado_en ASC."""
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("proyecto_id", str(proyecto_id))
        .order("creado_en", desc=False)
        .execute()
    )
    return response.data


async def update(area_id: str, campos: dict) -> dict | None:
    """
    Actualiza los campos indicados de un área y retorna el registro actualizado.
    Retorna None si el área no existe.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .update(campos)
        .eq("id", str(area_id))
        .execute()
    )
    return response.data[0] if response.data else None
