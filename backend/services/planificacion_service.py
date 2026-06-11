from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from repositories import planificacion_area_repo, planificacion_repo, planificacion_tarea_repo
from services.planificacion_mpp_adapter import parse_cronograma
from utils.errors import AppError
from utils.logger import log

_ORIGEN_MAP = {".xml": "excel", ".mpp": "mpp"}

AREA_COLORS = [
    "#3B82F6",  # azul
    "#8B5CF6",  # violeta
    "#06B6D4",  # cyan
    "#F97316",  # naranja
    "#EC4899",  # rosa
    "#6366F1",  # indigo
    "#14B8A6",  # teal
    "#A855F7",  # púrpura
]


async def run_importacion(
    proyecto_id: str,
    filename: str,
    file_bytes: bytes,
    archivo_url: str,
) -> None:
    """
    Orquesta el pipeline de importación de un cronograma de proyecto.

    Ejecuta en orden:
    1. parse_cronograma → normaliza el archivo a {proyecto, areas, tareas}.
    2. Pasada 1: inserta áreas y construye el mapa cap_wbs → area_id.
    3. Pasada 2: asigna area_id y proyecto_id a cada tarea, llama a upsert_bulk.
    4. update_resultado → marca el proyecto como 'listo' con origen y fechas.

    Si cualquier paso falla, registra estado='error' con el detalle del fallo.
    No relanza la excepción — corre como BackgroundTask.

    Args:
        proyecto_id: UUID del proyecto ya insertado con estado='procesando'.
        filename: Nombre del archivo original. Determina el origen:
            .xml → 'excel', .mpp → 'mpp'.
        file_bytes: Contenido binario del archivo.
        archivo_url: URL pública del archivo en el bucket 'cronogramas'.
    """
    try:
        cronograma = await parse_cronograma(filename, file_bytes)

        # Pasada 1: insertar áreas y construir mapa cap_wbs → area_id
        cap_wbs_to_area_id: dict[str, str] = {}
        for i, area in enumerate(cronograma["areas"]):
            color = AREA_COLORS[i % len(AREA_COLORS)]
            registro = await planificacion_area_repo.create(
                proyecto_id=proyecto_id,
                nombre=area["nombre"],
                cap_wbs=area["wbs"],
                color=color,
            )
            cap_wbs_to_area_id[area["wbs"]] = registro["id"]

        # Pasada 2: asignar area_id y proyecto_id a cada tarea, luego upsert bulk
        tareas: list[dict] = []
        for tarea in cronograma["tareas"]:
            tarea["area_id"] = cap_wbs_to_area_id.get(tarea.pop("cap_wbs"))
            tarea["proyecto_id"] = str(proyecto_id)
            tareas.append(tarea)
        await planificacion_tarea_repo.upsert_bulk(tareas)

        ext = Path(filename).suffix.lower()
        origen = _ORIGEN_MAP.get(ext, "excel")
        proy = cronograma["proyecto"]
        await planificacion_repo.update_resultado(
            proyecto_id=proyecto_id,
            origen=origen,
            archivo_url=archivo_url,
            fecha_inicio=proy.get("fecha_inicio"),
            fecha_fin=proy.get("fecha_fin"),
        )
        log.info(f"planificacion.completed | id={proyecto_id}")

    except Exception as exc:
        await planificacion_repo.update_error(str(proyecto_id), str(exc))
        log.error(f"planificacion.failed | id={proyecto_id} | error={exc}")


async def crear_area(
    proyecto_id: str,
    nombre: str,
    cap_wbs: str | None,
    responsable_nombre: str | None = None,
    responsable_telefono: str | None = None,
    responsable_email: str | None = None,
    disponibilidad_horas: int | None = None,
    cantidad_empleados: int | None = None,
) -> dict:
    """
    Crea un área manualmente en un proyecto existente.

    Asigna un color de la paleta AREA_COLORS según el índice de áreas ya
    existentes en el proyecto, evitando repetir colores mientras el total
    de áreas sea menor que len(AREA_COLORS).

    Args:
        proyecto_id: UUID del proyecto al que pertenece el área.
        nombre: Nombre del área (requerido).
        cap_wbs: Código WBS del nodo capítulo, p. ej. "1.2" (opcional).
        responsable_nombre: Nombre del responsable del área (opcional).
        responsable_telefono: Teléfono del responsable (opcional).
        responsable_email: Correo del responsable (opcional).
        disponibilidad_horas: Horas disponibles del equipo (opcional).
        cantidad_empleados: Número de empleados del área (opcional).

    Returns:
        El dict de la fila del área recién creada.
    """
    areas_existentes = await planificacion_area_repo.find_by_proyecto(proyecto_id)
    color = AREA_COLORS[len(areas_existentes) % len(AREA_COLORS)]
    return await planificacion_area_repo.create(
        proyecto_id=proyecto_id,
        nombre=nombre,
        cap_wbs=cap_wbs,
        color=color,
        responsable_nombre=responsable_nombre,
        responsable_telefono=responsable_telefono,
        responsable_email=responsable_email,
        disponibilidad_horas=disponibilidad_horas,
        cantidad_empleados=cantidad_empleados,
    )


async def marcar_tarea(
    tarea_id: str,
    proyecto_id: str,
    completada: bool,
    usuario_id: str,
) -> dict | None:
    """
    Marca o desmarca una tarea como completada, verificando pertenencia al proyecto.

    Confirma que tarea_id existe dentro de proyecto_id antes de escribir. Si no
    existe o pertenece a otro proyecto, lanza 404. Si completada=True, registra
    el timestamp UTC y el UUID del usuario; si False, limpia ambos campos.

    Args:
        tarea_id: UUID de la tarea a actualizar.
        proyecto_id: UUID del proyecto al que debe pertenecer la tarea.
        completada: Nuevo estado de completitud.
        usuario_id: UUID del usuario autenticado que realiza la acción.

    Returns:
        El dict de la fila actualizada, o None si el repo no devuelve datos.

    Raises:
        AppError(NOT_FOUND, 404): Si la tarea no existe o no pertenece al proyecto.
    """
    tarea = await planificacion_tarea_repo.find_by_id_and_proyecto(tarea_id, proyecto_id)
    if tarea is None:
        raise AppError("Tarea no encontrada", "NOT_FOUND", 404)
    completada_en: str | None = None
    completada_por: str | None = None
    if completada:
        completada_en = datetime.now(timezone.utc).isoformat()
        completada_por = usuario_id
    return await planificacion_tarea_repo.marcar_tarea(
        tarea_id=tarea_id,
        completada=completada,
        completada_en=completada_en,
        completada_por=completada_por,
    )
