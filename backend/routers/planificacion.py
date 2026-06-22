from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, Response, UploadFile

from controllers import planificacion_controller
from middleware.auth import get_current_user, require_admin
from schemas.planificacion import ActualizarProgresoRequest, AreaAsignacionRequest, AreaCreateRequest, AreaResponse, AreaUpdateRequest, AsignarDuenoAreaRequest, MarcarTareaRequest, ProyectoDetalleResponse, ProyectoResponse, ReprogramarTareaRequest, TareaResponse
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
    """Importa un cronograma y crea un proyecto de planificación en background.
    Raises: 400 formato no soportado · 401 no autenticado · 429 rate limit."""
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
    """Retorna el estado de un proyecto; endpoint de polling hasta estado != 'procesando'.
    Raises: 401 no autenticado · 404 no encontrado o sin acceso."""
    proyecto = await planificacion_controller.obtener_proyecto(str(proyecto_id), current_user)
    return ProyectoResponse(**proyecto)


@router.get("/{proyecto_id}/detalle", response_model=ProyectoDetalleResponse)
async def get_proyecto_detalle(
    proyecto_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ProyectoDetalleResponse:
    """Retorna proyecto + áreas + tareas; endpoint principal para las visuales.
    Raises: 401 no autenticado · 404 no encontrado o sin acceso."""
    return await planificacion_controller.obtener_detalle(str(proyecto_id), current_user)


@router.post("/{proyecto_id}/areas", response_model=AreaResponse, status_code=201)
async def crear_area(
    proyecto_id: UUID,
    payload: AreaCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> AreaResponse:
    """Crea un área manualmente en un proyecto existente.
    Raises: 401 no autenticado · 404 proyecto no encontrado o sin acceso."""
    resultado = await planificacion_controller.crear_area(str(proyecto_id), payload, current_user)
    return AreaResponse(**resultado)


@router.patch("/{proyecto_id}/areas/{area_id}", response_model=AreaResponse)
async def actualizar_area(
    proyecto_id: UUID,
    area_id: UUID,
    payload: AreaUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> AreaResponse:
    """Actualiza datos de contacto y disponibilidad de un área.
    Raises: 401 no autenticado · 404 proyecto o área no encontrada / sin acceso."""
    resultado = await planificacion_controller.actualizar_area(
        str(proyecto_id), str(area_id), payload.model_dump(exclude_none=True), current_user
    )
    return AreaResponse(**resultado)


@router.patch("/{proyecto_id}/areas/{area_id}/dueno", response_model=AreaResponse)
async def asignar_dueno_area(
    proyecto_id: UUID,
    area_id: UUID,
    payload: AsignarDuenoAreaRequest,
    current_user: dict = Depends(get_current_user),
) -> AreaResponse:
    """Asigna, cambia o desasigna el gerente dueño de un área (admin-only).
    Raises: 403 no admin · 404 área de otro proyecto/inexistente o gerente inexistente · 409 no es gerente."""
    require_admin(current_user)
    resultado = await planificacion_controller.asignar_dueno_area(
        str(proyecto_id), str(area_id), payload.gerente_id
    )
    return AreaResponse(**resultado)


@router.patch("/{proyecto_id}/tareas/{tarea_id}", response_model=TareaResponse)
async def marcar_tarea(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: MarcarTareaRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """Marca o desmarca una tarea como completada.
    Raises: 401 no autenticado · 404 proyecto o tarea no encontrada / sin acceso."""
    return await planificacion_controller.marcar_tarea(
        str(proyecto_id), str(tarea_id), payload.completada, current_user
    )


@router.patch("/{proyecto_id}/tareas/{tarea_id}/progreso", response_model=TareaResponse)
async def actualizar_progreso(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: ActualizarProgresoRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """Actualiza el progreso porcentual de una tarea (0, 25, 50, 75 o 100).
    Raises: 401 no autenticado · 404 proyecto o tarea no encontrada / sin acceso."""
    return await planificacion_controller.actualizar_progreso(
        str(proyecto_id), str(tarea_id), payload.progreso, current_user
    )


@router.patch("/{proyecto_id}/tareas/{tarea_id}/reprogramar", response_model=TareaResponse)
async def reprogramar_tarea(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: ReprogramarTareaRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """Actualiza las fechas de una tarea; registra las originales en la primera reprogramación.
    Raises: 401 no autenticado · 404 proyecto o tarea no encontrada / sin acceso."""
    return await planificacion_controller.reprogramar_tarea(
        str(proyecto_id), str(tarea_id), payload.fecha_inicio, payload.fecha_fin, current_user
    )


@router.patch("/{proyecto_id}/tareas/{tarea_id}/area", response_model=TareaResponse)
async def asignar_area_tarea(
    proyecto_id: UUID,
    tarea_id: UUID,
    payload: AreaAsignacionRequest,
    current_user: dict = Depends(get_current_user),
) -> TareaResponse:
    """Asigna o desasigna un área a una tarea individual.
    Raises: 401 no autenticado · 404 proyecto o tarea no encontrada / sin acceso."""
    resultado = await planificacion_controller.asignar_area_tarea(
        str(proyecto_id), str(tarea_id), payload.area_id, current_user
    )
    return TareaResponse(**resultado)


@router.delete("/{proyecto_id}", status_code=204)
async def eliminar_proyecto(
    proyecto_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Elimina un proyecto de planificación.
    Raises: 401 no autenticado · 404 no encontrado o sin acceso."""
    await planificacion_controller.eliminar_proyecto(str(proyecto_id), current_user)
    return Response(status_code=204)
