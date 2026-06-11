from __future__ import annotations

import asyncio

from fastapi import BackgroundTasks, UploadFile

from repositories import planificacion_area_repo, planificacion_repo, planificacion_tarea_repo
from schemas.planificacion import ProyectoDetalleResponse, ProyectoResponse, TareaResponse
from services.planificacion_service import marcar_tarea as service_marcar_tarea, run_importacion
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
    """
    Orquesta la creación de un proyecto de planificación.

    Lee el archivo, crea el registro en DB con estado='procesando', sube el
    archivo al bucket 'cronogramas' y lanza run_importacion como BackgroundTask.

    Returns:
        ProyectoResponse con estado='procesando'.
    """
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
    """
    Retorna el detalle completo de un proyecto (proyecto + áreas + tareas).

    Verifica ownership: si el proyecto no existe o el usuario no es propietario,
    retorna 404 — nunca 403 (SEGURIDAD: no confirmar existencia).
    """
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
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
    """
    Verifica ownership del proyecto y actualiza los campos del área.

    Verifica que el proyecto existe y pertenece al usuario autenticado antes de
    proceder. Nunca retorna 403 — usa 404 en ambos casos para no confirmar
    existencia de recursos ajenos.

    Args:
        proyecto_id: UUID del proyecto.
        area_id: UUID del área a actualizar.
        campos: Dict con los campos a actualizar (parcial, excluye nulos).
        current_user: Dict del usuario autenticado con clave 'sub'.

    Returns:
        Dict con los datos del área actualizada.

    Raises:
        AppError(NOT_FOUND, 404): Proyecto no existe, no es del usuario, o área no encontrada.
    """
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
    """
    Verifica ownership del proyecto y delega el marcado al service.

    Verifica que el proyecto existe y pertenece al usuario autenticado antes de
    proceder. Nunca retorna 403 — usa 404 en ambos casos para no confirmar
    existencia de recursos ajenos.

    Args:
        proyecto_id: UUID del proyecto.
        tarea_id: UUID de la tarea a marcar.
        completada: Nuevo estado de completitud.
        current_user: Dict del usuario autenticado con clave 'sub'.

    Returns:
        TareaResponse con los datos actualizados.

    Raises:
        AppError(NOT_FOUND, 404): Proyecto no existe, no es del usuario, o tarea no encontrada.
    """
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    resultado = await service_marcar_tarea(tarea_id, proyecto_id, completada, current_user["sub"])
    return TareaResponse(**resultado)


async def eliminar_proyecto(proyecto_id: str, current_user: dict) -> None:
    """
    Elimina un proyecto de planificación y sus datos asociados en cascada.
    Ownership: find_by_id → 404 si no existe → 404 si usuario_id no coincide.

    Args:
        proyecto_id: UUID del proyecto a eliminar.
        current_user: Dict del usuario autenticado con clave 'sub'.

    Raises:
        AppError(NOT_FOUND, 404): Proyecto no existe o no pertenece al usuario.
    """
    proyecto = await planificacion_repo.find_by_id(proyecto_id)
    if proyecto is None:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    if proyecto["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", "NOT_FOUND", 404)
    await planificacion_repo.delete_by_id(proyecto_id)
