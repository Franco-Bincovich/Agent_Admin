from __future__ import annotations

from services.gamma_service import publish_presentation
from integrations.supabase_client import get_supabase
from repositories import generation_repo
from services.ai_service import generate_outline
from services.prompt_builder import build_prompt
from services.image_extraction_service import extract_images_from_file
from services.pptx_service import generate_pptx
from utils.errors import AppError, ErrorCode
from utils.logger import log

_PPTX_BUCKET = "pptx-generados"
_VALID_OUTPUTS = {"pptx", "gamma", "ambos"}


def _upload_pptx(generation_id: str, pptx_bytes: bytes) -> str:
    """
    Sube los bytes del PPTX al bucket de Supabase Storage y retorna la URL pública.

    Args:
        generation_id: UUID usado como nombre de archivo ({generation_id}.pptx).
        pptx_bytes: Contenido binario del archivo PPTX.

    Returns:
        URL pública del archivo en Supabase Storage.
    """
    path = f"{generation_id}.pptx"
    storage = get_supabase().storage.from_(_PPTX_BUCKET)
    storage.upload(
        path=path,
        file=pptx_bytes,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        },
    )
    return storage.get_public_url(path)


def run_generation(
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
    """
    try:
        if output not in _VALID_OUTPUTS:
            raise AppError(
                f"output inválido: '{output}'. Válidos: pptx, gamma, ambos.",
                ErrorCode.INVALID_OUTPUT,
                400,
            )

        prompt = build_prompt(texto_extraido, objetivo, informacion_adicional, template, tono, audiencia)
        outline = generate_outline(prompt)

        pptx_url: str | None = None
        if output in ("pptx", "ambos"):
            imagenes: list[bytes] = []
            if usar_imagenes_documento and archivo_bytes:
                for nombre, contenido in archivo_bytes:
                    imagenes.extend(extract_images_from_file(nombre, contenido))
                log.info(
                    "Imágenes extraídas del documento",
                    extra={"cantidad": len(imagenes), "generation_id": str(generation_id)},
                )
            pptx_bytes = generate_pptx(outline, template, logo_bytes, imagenes)
            pptx_url = _upload_pptx(generation_id, pptx_bytes)

        gamma_url: str | None = None
        pptx_gamma_url: str | None = None
        if output in ("gamma", "ambos"):
            gamma_url, pptx_gamma_url = publish_presentation(
                outline, tema_visual, estilo_imagen, paleta_colores, cantidad_slides,
            )

        generation_repo.update_resultado(
            generation_id, pptx_url, gamma_url, pptx_gamma_url,
            len(outline["slides"]), outline,
        )
        log.info(f"generation.completed | id={generation_id}")
    except Exception as exc:
        generation_repo.update_error(generation_id)
        log.error(f"generation.failed | id={generation_id} | error={exc}")
