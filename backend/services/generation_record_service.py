from __future__ import annotations

import asyncio

from repositories import generation_repo
from repositories.user_repo import find_by_id as find_user_by_id
from services.extraction_service import extract_text_from_file
from utils.errors import AppError, ErrorCode
from utils.logger import log


async def create_generation_record(
    user_id: str,
    objetivo: str,
    filenames: list[str],
    parametros: dict,
    titulo: str = "",
) -> dict:
    """
    Inserta un registro de generación con estado='procesando' en la DB.

    Args:
        user_id: UUID del usuario que inicia la generación.
        objetivo: Objetivo declarado de la presentación.
        filenames: Lista de nombres de los archivos fuente.
        parametros: Dict con los parámetros de generación (template, tono, etc.).
        titulo: Título opcional de la presentación.

    Returns:
        Dict con los datos del registro creado, incluyendo el ID asignado.
    """
    return await generation_repo.create(user_id, objetivo, filenames, parametros, titulo)


async def list_all_generations() -> list[dict]:
    """Retorna todos los registros de generación. Solo para administradores."""
    return await generation_repo.find_all()


async def list_user_generations(user_id: str) -> list[dict]:
    """Retorna los registros de generación del usuario indicado."""
    log.info("list_user_generations llamado", extra={"user_id": str(user_id)})
    return await generation_repo.find_by_user(user_id)


async def get_generation_by_id(
    generation_id: str,
    user_id: str,
    is_admin: bool = False,
) -> dict:
    """
    Retorna una generación verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).

    Args:
        generation_id: UUID de la generación a buscar.
        user_id: UUID del usuario autenticado (del JWT).
        is_admin: True si el usuario tiene rol administrador.

    Returns:
        Dict con los datos de la generación.

    Raises:
        AppError: code NOT_FOUND (404) si no existe o el usuario no tiene acceso.
    """
    gen = await generation_repo.find_by_id(generation_id)
    if not gen:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    if not is_admin and gen["usuario_id"] != user_id:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return gen


async def prepare_generation_params(
    archivos: list,
    logo,
    objetivo: str,
    informacion_adicional: str | None,
    template: str,
    tono: str,
    audiencia: str,
    output: str,
    usar_imagenes: bool,
    tema_visual: str,
    estilo_imagen: str,
    paleta_colores: str,
    cantidad_slides: int,
    titulo: str | None,
    current_user: dict,
) -> dict:
    """
    Prepara todos los parámetros necesarios para lanzar una generación.
    Lee archivos, extrae texto, obtiene datos del usuario y construye
    el dict de parámetros para run_generation.

    Args:
        archivos: Lista de UploadFile con los archivos fuente.
        logo: UploadFile opcional del logo.
        objetivo: Objetivo principal de la presentación.
        informacion_adicional: Contexto extra opcional.
        template: Nombre del template visual.
        tono: Tono de comunicación.
        audiencia: Audiencia objetivo.
        output: Formato de salida (pptx/gamma/ambos).
        usar_imagenes: Si se deben incluir imágenes.
        tema_visual: Tema visual para Gamma.
        estilo_imagen: Estilo de imagen para Gamma.
        paleta_colores: Paleta de colores para Gamma.
        cantidad_slides: Cantidad de slides.
        titulo: Título personalizado opcional.
        current_user: Payload JWT del usuario autenticado.

    Returns:
        Dict con todos los parámetros listos para run_generation.
    """
    textos = []
    archivo_bytes = []
    for archivo in archivos:
        contenido = await archivo.read()
        texto = await asyncio.to_thread(
            extract_text_from_file, archivo.filename or "", contenido
        )
        textos.append(texto)
        archivo_bytes.append((archivo.filename or "", contenido))

    texto_extraido = "\n\n".join(textos)

    logo_bytes: bytes | None = None
    if logo:
        logo_bytes = await logo.read()

    user = await find_user_by_id(current_user["sub"]) or {}
    user_email: str = user.get("email", "")
    gamma_folder_id: str | None = user.get("gamma_folder_id")

    return {
        "texto_extraido": texto_extraido,
        "archivo_bytes": archivo_bytes,
        "logo_bytes": logo_bytes,
        "user_email": user_email,
        "gamma_folder_id": gamma_folder_id,
        "parametros": {
            "template": template,
            "tono": tono,
            "audiencia": audiencia,
            "output": output,
            "informacion_adicional": informacion_adicional,
            "usar_imagenes": usar_imagenes,
            "tema_visual": tema_visual,
            "estilo_imagen": estilo_imagen,
            "paleta_colores": paleta_colores,
            "cantidad_slides": cantidad_slides,
            "titulo": titulo,
            "objetivo": objetivo,
        },
    }
