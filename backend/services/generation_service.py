from __future__ import annotations

import asyncio

from services.gamma_service import publish_presentation, resolve_user_folder
from repositories import generation_repo
from services.ai_service import generate_outline
from services.generation_storage import _upload_pptx
from services.prompt_builder import build_prompt
from services.image_extraction_service import extract_images_from_file, extract_docx_pages_as_images
from services.pptx_service import generate_pptx
from utils.errors import AppError, ErrorCode
from utils.logger import log

_VALID_OUTPUTS = {"pptx", "gamma", "ambos"}


async def run_generation(
    generation_id: str,
    texto_extraido: str,
    objetivo: str,
    informacion_adicional: str | None,
    template: str,
    tono: str,
    audiencia: str,
    logo_bytes: bytes | None = None,
    output: str = "ambos",
    usar_imagenes_documento: bool = False,
    archivo_bytes: list[tuple[str, bytes]] | None = None,
    tema_visual: str = "minimalist",
    estilo_imagen: str = "aiGenerated",
    paleta_colores: str = "",
    cantidad_slides: int = 10,
    titulo: str = "",
    user_id: str = "",
    user_email: str = "",
    gamma_folder_id: str | None = None,
) -> None:
    """
    Orquesta el pipeline completo de generación de presentaciones.

    Ejecuta en orden: validación de output → build_prompt → generate_outline →
    [generate_pptx + Supabase upload] → [publish_to_gamma] → DB update_resultado.
    Los pasos de PPTX y Gamma son condicionales según el valor de `output`.

    Si cualquier paso falla, registra estado='error' en la DB y loguea con
    log.error. No relanza la excepción — el pipeline corre en background.

    Args:
        generation_id: UUID de la generación ya insertada con estado='procesando'.
        texto_extraido: Texto concatenado de todos los archivos fuente.
        objetivo: Objetivo declarado de la presentación.
        informacion_adicional: Contexto adicional del usuario (puede ser None).
        template: Nombre del template PPTX. Ver TemplateEnum en schemas/generation.py.
        tono: Tono de la presentación. Ver ToneEnum.
        audiencia: Audiencia objetivo. Ver AudienceEnum.
        logo_bytes: Bytes del logo (puede ser None).
        output: Tipo de output requerido. Valores: 'pptx' | 'gamma' | 'ambos'.
            'pptx'  → genera sólo PPTX, saltea Gamma.
            'gamma' → genera sólo Gamma, saltea PPTX.
            'ambos' → genera ambos (comportamiento por defecto).
        usar_imagenes_documento: Si True y output incluye 'pptx', extrae imágenes
            de cada archivo fuente e intenta incluirlas en el PPTX. Si no se
            extraen imágenes, el PPTX se genera sin ellas sin lanzar error.
        archivo_bytes: Lista de tuplas (nombre_archivo, bytes) de cada archivo fuente.
            Requerido cuando usar_imagenes_documento=True para la extracción de imágenes.
        tema_visual: Tema visual de Gamma pasado como 'style' en el MCP. Ver TemaVisualEnum.
        estilo_imagen: Fuente de imágenes de Gamma pasado como 'imageOptions.source'.
        paleta_colores: Paleta de colores sugerida. Se incluye en el prompt de Gamma.
        cantidad_slides: Cantidad objetivo de slides pasada como 'numCards' en el MCP (5-20).
        user_id: UUID del usuario, necesario para cachear el folder_id de Gamma si se resuelve.
        user_email: Email del usuario, usado como nombre de carpeta en Gamma.
        gamma_folder_id: ID de carpeta Gamma ya cacheado en DB; si es None se intenta resolver.
    """
    try:
        if output not in _VALID_OUTPUTS:
            raise AppError(
                f"output inválido: '{output}'. Válidos: pptx, gamma, ambos.",
                ErrorCode.INVALID_OUTPUT,
                400,
            )

        imagenes: list[bytes] = []
        if usar_imagenes_documento and archivo_bytes:
            for nombre, contenido in archivo_bytes:
                imgs = extract_images_from_file(nombre, contenido)
                log.info(
                    f"img.extract | archivo={nombre} | "
                    f"bytes={len(contenido)} | "
                    f"extraidas={len(imgs)} | "
                    f"id={generation_id}"
                )
                imagenes.extend(imgs)
            # Deduplicar por hash de contenido
            seen: set[int] = set()
            imagenes_unicas: list[bytes] = []
            for img in imagenes:
                h = hash(img)
                if h not in seen:
                    seen.add(h)
                    imagenes_unicas.append(img)
            imagenes = imagenes_unicas[:20]
            log.info(
                f"img.total | cantidad={len(imagenes)} | id={generation_id}"
            )

        paginas_docx: list[bytes] = []
        if archivo_bytes:
            for nombre, contenido in archivo_bytes:
                if nombre.lower().endswith(".docx"):
                    pages = extract_docx_pages_as_images(contenido)
                    paginas_docx.extend(pages)
                    if pages:
                        log.info(
                            f"docx.pages | archivo={nombre} | "
                            f"paginas={len(pages)} | id={generation_id}"
                        )

        prompt = build_prompt(
            texto_extraido, objetivo, informacion_adicional,
            template, tono, audiencia,
            cantidad_slides=cantidad_slides,
        )
        outline = await generate_outline(
            prompt,
            imagenes=imagenes if imagenes else None,
            imagenes_contenido=paginas_docx if paginas_docx else None,
        )

        pptx_url: str | None = None
        if output in ("pptx", "ambos"):
            pptx_bytes = await asyncio.to_thread(
                generate_pptx, outline, template, logo_bytes, imagenes
            )
            pptx_url = await asyncio.to_thread(
                _upload_pptx, generation_id, pptx_bytes
            )

        gamma_url: str | None = None
        pptx_gamma_url: str | None = None
        gamma_warning: str | None = None
        if output in ("gamma", "ambos"):
            folder_id = gamma_folder_id
            if folder_id is None and user_email:
                folder_id, gamma_warning = await resolve_user_folder(user_email, user_id)
            try:
                result = await publish_presentation(
                    outline, tema_visual, estilo_imagen, paleta_colores, cantidad_slides, titulo,
                    folder_id,
                )
                gamma_url = result["gamma_url"]
                pptx_gamma_url = result["pptx_gamma_url"]
            except AppError as exc:
                log.warning(f"gamma.skipped | id={generation_id} | error={exc}")

        await generation_repo.update_resultado(
            generation_id, pptx_url, gamma_url, pptx_gamma_url,
            len(outline["slides"]), outline, gamma_warning,
        )
        log.info(f"generation.completed | id={generation_id}")
    except Exception as exc:
        await generation_repo.update_error(generation_id)
        log.error(f"generation.failed | id={generation_id} | error={exc}")
