import asyncio

from fastapi import BackgroundTasks, UploadFile

from repositories import planificacion_area_repo, planificacion_repo, planificacion_tarea_repo
from schemas.planificacion import AreaCreateRequest, ProyectoDetalleResponse, ProyectoResponse, TareaResponse
from services.planificacion_service import crear_area as service_crear_area, run_importacion
from services.planificacion_tarea_service import actualizar_progreso as service_actualizar_progreso, marcar_tarea as service_marcar_tarea, reprogramar_tarea as service_reprogramar_tarea
from services.planificacion_storage import upload_cronograma
from utils.errors import AppError


async def crear_proyecto(
    background_tasks: BackgroundTasks,
    archivo: UploadFile,
    nombre: str,
    expediente: str | None,
    prioridad: str,
    current_user: dict,
) -> ProyectoResponse:
    """Crea un proyecto de planificación en background; retorna estado='procesando'."""
    file_bytes = await archivo.read()
    proyecto = await planificacion_repo.create(
        current_user["sub"], nombre, expediente, prioridad
    )
    archivo_url = await asyncio.to_thread(
        upload_cronograma, proyecto["id"], archivo.filename, file_bytes
    )
    background_tasks.add_task(
        run_importacion, proyecto["id"], archivo.filename, file_bytes, archivo_url
    )
    return ProyectoResponse(**proyecto)


async def obtener_detalle(
    proyecto_id: str,
    current_user: dict,
) -> ProyectoDetalleResponse:
    """Retorna proyecto + áreas + tareas completos (lectura compartida). 404 solo si no existe."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    areas, tareas = await asyncio.gather(
        planificacion_area_repo.find_by_proyecto(proyecto_id),
        planificacion_tarea_repo.find_by_proyecto(proyecto_id),
    )
    return ProyectoDetalleResponse(**proyecto, areas=areas, tareas=tareas)


async def actualizar_area(
    proyecto_id: str,
    area_id: str,
    campos: dict,
    current_user: dict,
) -> dict:
    """Actualiza los campos del área verificando ownership del proyecto. Verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    resultado = await planificacion_area_repo.update(area_id, campos)
    if resultado is None:
        raise AppError("Área no encontrada", "NOT_FOUND", 404)
    return resultado


async def marcar_tarea(
    proyecto_id: str,
    tarea_id: str,
    completada: bool,
    current_user: dict,
) -> TareaResponse:
    """Delega el marcado de tarea al service verificando ownership del proyecto. Verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    resultado = await service_marcar_tarea(tarea_id, proyecto_id, completada, current_user["sub"])
    return TareaResponse(**resultado)


async def actualizar_progreso(
    proyecto_id: str,
    tarea_id: str,
    progreso: int,
    current_user: dict,
) -> TareaResponse:
    """Delega la actualización de progreso al service verificando ownership del proyecto. Verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    resultado = await service_actualizar_progreso(tarea_id, proyecto_id, progreso, current_user["sub"])
    return TareaResponse(**resultado)


async def reprogramar_tarea(
    proyecto_id: str,
    tarea_id: str,
    fecha_inicio: str,
    fecha_fin: str,
    current_user: dict,
) -> TareaResponse:
    """Reprograma las fechas de una tarea verificando ownership del proyecto. Verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    resultado = await service_reprogramar_tarea(tarea_id, proyecto_id, fecha_inicio, fecha_fin)
    return TareaResponse(**resultado)


async def eliminar_proyecto(proyecto_id: str, current_user: dict) -> None:
    """Elimina un proyecto y sus datos en cascada; verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    await planificacion_repo.delete_by_id(proyecto_id)


async def listar_proyectos(current_user: dict) -> list[dict]:
    """Retorna todos los proyectos de planificación (lectura compartida entre usuarios autenticados)."""
    return await planificacion_repo.find_all()


async def obtener_proyecto(proyecto_id: str, current_user: dict) -> dict:
    """Retorna un proyecto por ID (lectura compartida). 404 solo si no existe."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    return proyecto


async def crear_area(
    proyecto_id: str,
    payload: AreaCreateRequest,
    current_user: dict,
) -> dict:
    """Crea un área nueva en el proyecto. Verifica ownership (404 si no existe o no es del usuario)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None or proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    return await service_crear_area(
        proyecto_id=proyecto_id,
        nombre=payload.nombre,
        cap_wbs=payload.cap_wbs,
        responsable_nombre=payload.responsable_nombre,
        responsable_telefono=payload.responsable_telefono,
        responsable_email=payload.responsable_email,
        disponibilidad_horas=payload.disponibilidad_horas,
        cantidad_empleados=payload.cantidad_empleados,
    )


async def asignar_area_tarea(
    proyecto_id: str,
    tarea_id: str,
    area_id: str | None,
    current_user: dict,
) -> dict:
    """Asigna o desasigna un área a una tarea. Verifica ownership del proyecto y tarea (404 en ambos casos)."""
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None or proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    resultado = await planificacion_tarea_repo.update_area(tarea_id, area_id)
    if resultado is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    return resultado
