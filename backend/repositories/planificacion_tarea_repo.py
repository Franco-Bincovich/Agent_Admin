from __future__ import annotations

import asyncio

from integrations.supabase_client import get_supabase

_TABLE = "planificacion_tareas"


def _db():
    return get_supabase().table(_TABLE)


async def upsert_bulk(tareas: list[dict]) -> list[dict]:
    """
    Inserta o actualiza tareas en bloque usando el UNIQUE (proyecto_id, wbs).
    En reimport: actualiza datos de scheduling (nombre, nivel, fechas, área).
    NO sobreescribe completada/completada_en/completada_por — el estado de avance
    marcado por el usuario se preserva aunque el cronograma se reimporte.
    Cada dict en tareas debe incluir: proyecto_id, wbs, nombre, nivel, es_resumen.
    Campos opcionales: area_id, fecha_inicio, fecha_fin, fecha_estimada, confianza, predecesoras.
    """
    if not tareas:
        return []
    response = await asyncio.to_thread(
        lambda: _db()
        .upsert(tareas, on_conflict="proyecto_id,wbs")
        .execute()
    )
    return response.data


async def find_by_proyecto(proyecto_id: str) -> list[dict]:
    """Retorna todas las tareas de un proyecto ordenadas por wbs ASC."""
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("proyecto_id", str(proyecto_id))
        .order("wbs", desc=False)
        .execute()
    )
    return response.data


async def find_by_id_and_proyecto(tarea_id: str, proyecto_id: str) -> dict | None:
    """
    Busca una tarea por su ID y el proyecto al que pertenece.

    Filtra simultáneamente por id y proyecto_id para garantizar que la tarea
    existe y pertenece al proyecto indicado. Retorna None si no hay coincidencia,
    lo que cubre tanto tarea inexistente como tarea de otro proyecto.

    Args:
        tarea_id: UUID de la tarea.
        proyecto_id: UUID del proyecto propietario.

    Returns:
        Dict con la fila de la tarea, o None si no existe o no pertenece al proyecto.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("id", str(tarea_id))
        .eq("proyecto_id", str(proyecto_id))
        .execute()
    )
    return response.data[0] if response.data else None


async def update_area(tarea_id: str, area_id: str | None) -> dict | None:
    """
    Actualiza únicamente el campo area_id de una tarea.

    Permite asignar la tarea a un área (area_id UUID como string) o
    desasignarla pasando area_id=None. No verifica pertenencia al proyecto;
    esa responsabilidad recae en la capa de router.

    Args:
        tarea_id: UUID de la tarea a actualizar.
        area_id: UUID del área a asignar, o None para desasignar.

    Returns:
        El dict de la fila actualizada, o None si la tarea no existe.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .update({"area_id": area_id})
        .eq("id", str(tarea_id))
        .execute()
    )
    return response.data[0] if response.data else None


async def actualizar_avance(
    tarea_id: str,
    progreso: int,
    completada: bool,
    completada_en: str | None,
    completada_por: str | None,
) -> dict | None:
    """Actualiza progreso y las columnas de completada sincronizadas. Retorna None si la tarea no existe."""
    response = await asyncio.to_thread(
        lambda: _db()
        .update({
            "progreso": progreso,
            "completada": completada,
            "completada_en": completada_en,
            "completada_por": completada_por,
        })
        .eq("id", str(tarea_id))
        .execute()
    )
    return response.data[0] if response.data else None
