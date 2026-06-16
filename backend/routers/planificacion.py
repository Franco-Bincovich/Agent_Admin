from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, Response, UploadFile

from controllers import planificacion_controller
from middleware.auth import get_current_user
from schemas.planificacion import AreaAsignacionRequest, AreaCreateRequest, AreaResponse, AreaUpdateRequest, MarcarTareaRequest, ProyectoDetalleResponse, ProyectoResponse, TareaResponse
from utils.limiter import limiter

router = APIRouter()


@router.post("", response_model=ProyectoResponse, status_code=202)
@limiter.limit("10/minute")
async def crear_proyecto(
    request: Request,
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(...),
    nombre: str = Form(..., min_length=3, max_length=200),
    expediente: str | None = Form(default=None),
    prioridad: str = Form(default="media"),
    current_user: dict = Depends(get_current_user),
) -> ProyectoResponse:
    """
    Importa un cronograma y crea un proyecto de planificación en background.

    Raises:
        400: Formato no soportado · 401: No autenticado · 429: Rate limit
    """
    return await planificacion_controller.crear_proyecto(
        background_tasks, archivo, nombre, expediente, prioridad, current_user
    )


@router.get("", response_model=list[ProyectoResponse])
async def listar_proyectos(
    current_user: dict = Depends(get_current_user),
) -> list[ProyectoResponse]:
    """Retorna los proyectos de planificación del usuario autenticado."""
    registros = await planificacion_controller.listar_proyectos(current_user)
    return [ProyectoResponse(**r) for r in registros]


@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def get_proyecto(
    proyecto_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ProyectoResponse:
    """
    Retorna el estado de un proyecto. Endpoint de polling hasta estado != 'procesando'.

    Raises:
        401: No autenticado · 404: No encontrado o sin acceso
    """
    proyecto = await planificacion_controller.obtener_proyecto(str(proyecto_id), current_user)
    return ProyectoResponse(**proyecto)


@router.get("/{proyecto_id}/detalle", response_model=ProyectoDetalleResponse)
async def get_proyecto_detalle(
    proyecto_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ProyectoDetalleResponse:
    """
    Retorna proyecto + áreas + tareas. Endpoint principal para las visuales.

    Raises:
        401: No autenticado · 404: No encontrado o sin acceso
    """
    return await planificacion_controller.obtener_detalle(str(proyecto_id), current_user)


@router.post("/{proyecto_id}/areas", response_model=AreaResponse, status_code=201)
async def crear_area(
    proyecto_id: UUID,
    payload: AreaCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> AreaResponse:
    """
    Crea un área manualmente en un proyecto existente.

    Raises:
        401: No autenticado · 404: Proyecto no encontrado o sin acceso
    """
    resultado = await planificacion_controller.crear_area(str(proyecto_id), payload, current_user)
    return AreaResponse(**resultado)


@router.patch("/{proyecto_id}/areas/{area_id}", response_model=AreaResponse)
async def actualizar_area(
    proyecto_id: UUID,
    area_id: UUID,
    payload: AreaUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> AreaResponse:
    """
    Actualiza datos de contacto y disponibilidad de un área.

    Raises:
        401: No autenticado · 404: Proyecto o área no encontrada / sin acceso
    """
    resultado = await planificacion_controller.actualizar_area(
        str(proyecto_id), str(area_id), payload.model_dump(exclude_none=True), current_user
    )
    return AreaResponse(**resultado)


@router.patch("/{proyecto_id}/tareas/{tarea_id}", response_model=TareaResponse)
async def marcar_tarea(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: MarcarTareaRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """
    Marca o desmarca una tarea como completada.

    Raises:
        401: No autenticado · 404: Proyecto o tarea no encontrada / sin acceso
    """
    return await planificacion_controller.marcar_tarea(
        str(proyecto_id), str(tarea_id), payload.completada, current_user
    )


@router.patch("/{proyecto_id}/tareas/{tarea_id}/area", response_model=TareaResponse)
async def asignar_area_tarea(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: AreaAsignacionRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """
    Asigna o desasigna un área a una tarea individual.

    Raises:
        401: No autenticado · 404: Proyecto o tarea no encontrada / sin acceso
    """
    resultado = await planificacion_controller.asignar_area_tarea(
        str(proyecto_id), str(tarea_id), payload.area_id, current_user
    )
    return TareaResponse(**resultado)


@router.delete("/{proyecto_id}", status_code=204)
async def eliminar_proyecto(
    proyecto_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """
    Elimina un proyecto de planificación.

    Raises:
        401: No autenticado · 404: No encontrado o sin acceso
    """
    await planificacion_controller.eliminar_proyecto(str(proyecto_id), current_user)
    return Response(status_code=204)
