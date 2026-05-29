from __future__ import annotations

from fastapi import BackgroundTasks, UploadFile

from schemas.generation import (
    AudienceEnum, EstiloImagenEnum, GenerationResponse, OutputEnum,
    TemplateEnum, TemaVisualEnum, ToneEnum,
)
from utils.logger import log
from services.generation_record_service import (
    create_generation_record,
    get_generation_by_id,
    list_all_generations,
    list_user_generations,
    prepare_generation_params,
)
from services.generation_service import run_generation


async def start_generation(
    background_tasks: BackgroundTasks,
    archivos: list[UploadFile],
    objetivo: str,
    informacion_adicional: str | None,
    template: TemplateEnum,
    tono: ToneEnum,
    audiencia: AudienceEnum,
    output: OutputEnum,
    logo: UploadFile | None,
    current_user: dict,
    usar_imagenes_documento: bool = False,
    tema_visual: TemaVisualEnum = TemaVisualEnum.minimalist,
    estilo_imagen: EstiloImagenEnum = EstiloImagenEnum.aiGenerated,
    paleta_colores: str = "",
    cantidad_slides: int = 10,
    titulo: str = "",
) -> GenerationResponse:
    """
    Orquesta el inicio de una generación: extrae texto, crea el registro en DB
    con estado='procesando' y lanza run_generation() como BackgroundTask.

    Returns:
        GenerationResponse con estado='procesando'.
    """
    params = await prepare_generation_params(
        archivos, logo, objetivo, informacion_adicional,
        template, tono, audiencia, output, usar_imagenes_documento,
        tema_visual, estilo_imagen, paleta_colores,
        cantidad_slides, titulo, current_user
    )
    gen = await create_generation_record(
        current_user["sub"], objetivo,
        [f.filename for f in archivos], params["parametros"],
        titulo,
    )
    background_tasks.add_task(
        run_generation,
        gen["id"], params["texto_extraido"], objetivo, informacion_adicional,
        template, tono, audiencia, params["logo_bytes"], output,
        usar_imagenes_documento, params["archivo_bytes"],
        tema_visual, estilo_imagen, paleta_colores, cantidad_slides,
        titulo,
        current_user["sub"], params["user_email"], params["gamma_folder_id"],
    )
    return GenerationResponse(**gen)


async def list_generations(current_user: dict) -> list[GenerationResponse]:
    """Retorna el historial de generaciones según el rol del usuario."""
    log.info("list_generations llamado", extra={"current_user": str(current_user)})
    if current_user.get("role") == "administrador":
        records = await list_all_generations()
    else:
        records = await list_user_generations(current_user["sub"])
    return [GenerationResponse(**r) for r in records]


async def get_generation(generation_id: str, current_user: dict) -> GenerationResponse:
    """
    Retorna una generación verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).
    """
    is_admin = current_user.get("role") == "administrador"
    gen = await get_generation_by_id(generation_id, current_user["sub"], is_admin)
    return GenerationResponse(**gen)
