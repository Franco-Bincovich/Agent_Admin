from datetime import datetime, timezone

from repositories import planificacion_tarea_repo
from utils.errors import AppError


def _sincronizar_completada(progreso: int, usuario_id: str) -> tuple[bool, str | None, str | None]:
    """Calcula completada, completada_en y completada_por a partir de progreso."""
    completada = progreso == 100
    if completada:
        return completada, datetime.now(timezone.utc).isoformat(), usuario_id
    return completada, None, None


async def marcar_tarea(
    tarea_id: str,
    proyecto_id: str,
    completada: bool,
    usuario_id: str,
) -> dict | None:
    """Marca/desmarca una tarea; verifica pertenencia al proyecto. Lanza 404 si no existe."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    progreso = 100 if completada else 0
    _completada, completada_en, completada_por = _sincronizar_completada(progreso, usuario_id)
    return await planificacion_tarea_repo.actualizar_avance(
        tarea_id=tarea_id,
        progreso=progreso,
        completada=_completada,
        completada_en=completada_en,
        completada_por=completada_por,
    )


async def actualizar_progreso(
    tarea_id: str,
    proyecto_id: str,
    progreso: int,
    usuario_id: str,
) -> dict:
    """Actualiza el progreso de una tarea; verifica pertenencia al proyecto. Lanza 404 si no existe."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    completada, completada_en, completada_por = _sincronizar_completada(progreso, usuario_id)
    return await planificacion_tarea_repo.actualizar_avance(
        tarea_id=tarea_id,
        progreso=progreso,
        completada=completada,
        completada_en=completada_en,
        completada_por=completada_por,
    )


async def reprogramar_tarea(
    tarea_id: str,
    proyecto_id: str,
    fecha_inicio: str,
    fecha_fin: str,
) -> dict:
    """Actualiza las fechas de una tarea preservando el plan base si ya fue reprogramada. Lanza 404 si no existe o no pertenece al proyecto."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    if not tarea["reprogramada"]:
        fecha_inicio_original = tarea["fecha_inicio"]
        fecha_fin_original = tarea["fecha_fin"]
    else:
        fecha_inicio_original = tarea["fecha_inicio_original"]
        fecha_fin_original = tarea["fecha_fin_original"]
    return await planificacion_tarea_repo.reprogramar_tarea(
        tarea_id=tarea_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fecha_inicio_original=fecha_inicio_original,
        fecha_fin_original=fecha_fin_original,
    )
