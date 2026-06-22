from datetime import datetime, timezone

from repositories import planificacion_tarea_repo
from services.planificacion_permisos import assert_puede_mutar_tarea
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
    current_user: dict,
) -> dict | None:
    """Marca/desmarca una tarea; verifica pertenencia y permiso de escritura. Lanza 404 si no existe, 403 si no puede."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    await assert_puede_mutar_tarea(tarea, current_user)
    progreso = 100 if completada else 0
    _completada, completada_en, completada_por = _sincronizar_completada(progreso, current_user["sub"])
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
    current_user: dict,
) -> dict:
    """Actualiza el progreso de una tarea; verifica pertenencia y permiso de escritura. Lanza 404 si no existe, 403 si no puede."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    await assert_puede_mutar_tarea(tarea, current_user)
    completada, completada_en, completada_por = _sincronizar_completada(progreso, current_user["sub"])
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
    current_user: dict,
) -> dict:
    """Actualiza las fechas de una tarea preservando el plan base si ya fue reprogramada. Verifica permiso de escritura. Lanza 404 si no existe/no pertenece, 403 si no puede."""
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    await assert_puede_mutar_tarea(tarea, current_user)
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
