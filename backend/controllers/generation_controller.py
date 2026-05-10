from __future__ import annotations

from fastapi import BackgroundTasks, UploadFile

from repositories import generation_repo
from schemas.generation import (
    AudienceEnum, EstiloImagenEnum, GenerationResponse, OutputEnum,
    TemplateEnum, TemaVisualEnum, ToneEnum,
)
from services.extraction_service import extract_text_from_file
from services.generation_service import run_generation
from utils.errors import AppError, ErrorCode


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
) -> GenerationResponse:
    """
    Orquesta el inicio de una generación: extrae texto, crea el registro en DB
    con estado='procesando' y lanza run_generation() como BackgroundTask.

    Returns:
        GenerationResponse con estado='procesando'.
    """
    textos, archivo_bytes = [], []
    for archivo in archivos:
        contenido = await archivo.read()
        textos.append(extract_text_from_file(archivo.filename or "", contenido))
        archivo_bytes.append((archivo.filename or "", contenido))
    texto_extraido = "\n\n".join(textos)

    logo_bytes: bytes | None = None
    if logo:
        logo_bytes = await logo.read()

    parametros = {
        "template": template, "tono": tono, "audiencia": audiencia,
        "output": output, "informacion_adicional": informacion_adicional,
        "usar_imagenes_documento": usar_imagenes_documento,
        "tema_visual": tema_visual, "estilo_imagen": estilo_imagen,
        "paleta_colores": paleta_colores, "cantidad_slides": cantidad_slides,
    }
    gen = generation_repo.create(
        current_user["sub"], objetivo,
        [f.filename for f in archivos], parametros,
    )
    background_tasks.add_task(
        run_generation,
        gen["id"], texto_extraido, objetivo, informacion_adicional,
        template, tono, audiencia, logo_bytes, output,
        usar_imagenes_documento, archivo_bytes,
        tema_visual, estilo_imagen, paleta_colores, cantidad_slides,
    )
    return GenerationResponse(**gen)


def list_generations(current_user: dict) -> list[GenerationResponse]:
    """Retorna el historial de generaciones según el rol del usuario."""
    if current_user.get("role") == "administrador":
        records = generation_repo.find_all()
    else:
        records = generation_repo.find_by_user(current_user["sub"])
    return [GenerationResponse(**r) for r in records]


def get_generation(generation_id: str, current_user: dict) -> GenerationResponse:
    """
    Retorna una generación verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).
    """
    gen = generation_repo.find_by_id(generation_id)
    if not gen:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    is_admin = current_user.get("role") == "administrador"
    if not is_admin and gen["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return GenerationResponse(**gen)
