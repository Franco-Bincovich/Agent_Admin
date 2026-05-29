from __future__ import annotations

import asyncio

from repositories import documento_mutations_repo, documento_repo
from services.documento_ai_service import _DEFAULT_SECCIONES, build_documento_prompt, generate_documento_outline
from services.documento_storage import _validate_storage_url, _download_file, _upload_docx
from services.docx_service import generate_docx
from services.extraction_service import extract_text_from_file
from services.image_extraction_service import extract_images_from_file
from utils.logger import log


async def run_document_generation(
    documento_id: str,
    archivos_urls: list[str],
    plantilla_url: str | None,
    logo_url: str | None,
    titulo: str,
    secciones: list[str],
    indicaciones: str | None,
    opciones: dict,
) -> None:
    """
    Orquesta el pipeline completo de unificación de documentos.

    Descarga los archivos desde Supabase Storage y luego ejecuta en orden:
    extracción de texto → extracción de imágenes (si usar_imagenes) →
    build_documento_prompt → generate_documento_outline → generate_docx →
    Supabase Storage upload → DB update_resultado.

    La plantilla DOCX (si se provee) se usa únicamente como molde visual en
    generate_docx — su texto NO se extrae ni influye en las secciones.

    Si cualquier paso falla, registra estado='error' en la DB y loguea con
    log.error. No relanza la excepción — el pipeline corre en background.

    Args:
        documento_id: UUID del documento ya insertado con estado='procesando'.
        archivos_urls: URLs de Supabase Storage de los archivos fuente.
        plantilla_url: URL de la plantilla DOCX base, o None.
        logo_url: URL del logo a insertar en la primera página, o None.
        titulo: Título del documento final.
        secciones: Secciones requeridas por el usuario.
        indicaciones: Indicaciones adicionales del usuario (puede ser None).
        opciones: Dict con homogeneizar, deduplicar, usar_imagenes.
    """
    try:
        archivos = [await _download_file(url) for url in archivos_urls]
        plantilla = await _download_file(plantilla_url) if plantilla_url else None
        logo_bytes = (await _download_file(logo_url))[1] if logo_url else None

        textos_extraidos: dict[str, str] = {}
        for nombre, file_bytes in archivos:
            textos_extraidos[nombre] = extract_text_from_file(nombre, file_bytes)

        plantilla_bytes: bytes | None = plantilla[1] if plantilla else None

        secciones = secciones if secciones else _DEFAULT_SECCIONES

        imagenes: list[tuple[str, bytes]] = []
        if opciones.get("usar_imagenes"):
            for nombre, file_bytes in archivos:
                for img_bytes in extract_images_from_file(nombre, file_bytes):
                    imagenes.append((nombre, img_bytes))
            # Deduplicar por hash de contenido
            seen = set()
            imagenes_unicas = []
            for nombre_img, img_bytes in imagenes:
                h = hash(img_bytes)
                if h not in seen:
                    seen.add(h)
                    imagenes_unicas.append((nombre_img, img_bytes))
            imagenes = imagenes_unicas[:20]  # máximo 20 imágenes
            if imagenes:
                log.info(
                    "Imágenes extraídas del documento",
                    extra={"cantidad": len(imagenes),
                           "documento_id": str(documento_id)},
                )

        prompt = build_documento_prompt(
            textos_extraidos, titulo, secciones,
            indicaciones, opciones,
        )
        imagenes_bytes = [img for _, img in imagenes] if imagenes else None
        outline = await generate_documento_outline(
            prompt,
            imagenes=imagenes_bytes if imagenes_bytes else None,
        )
        usar_imagenes = bool(opciones.get("usar_imagenes"))
        docx_bytes = await asyncio.to_thread(
            generate_docx, outline, imagenes, usar_imagenes,
            plantilla_bytes, logo_bytes
        )
        docx_url = await asyncio.to_thread(
            _upload_docx, documento_id, docx_bytes
        )
        await documento_mutations_repo.update_resultado(documento_id, docx_url)
        log.info(f"documento.completed | id={documento_id}")

    except Exception as exc:
        await documento_mutations_repo.update_error(documento_id)
        log.error(f"documento.failed | id={documento_id} | error={exc}")
