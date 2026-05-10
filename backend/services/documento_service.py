from __future__ import annotations

from integrations.supabase_client import get_supabase
from repositories import documento_mutations_repo, documento_repo
from services.documento_ai_service import _DEFAULT_SECCIONES, build_documento_prompt, generate_documento_outline
from services.docx_service import generate_docx
from services.extraction_service import extract_text_from_file
from services.image_extraction_service import extract_images_from_file
from utils.errors import AppError
from utils.logger import log

_DOCX_BUCKET = "docx-generados"


def _upload_docx(documento_id: str, docx_bytes: bytes) -> str:
    """
    Sube los bytes del DOCX al bucket de Supabase Storage y retorna la URL pública.

    Args:
        documento_id: UUID usado como nombre de archivo ({documento_id}.docx).
        docx_bytes: Contenido binario del archivo DOCX.

    Returns:
        URL pública del archivo en Supabase Storage.
    """
    path = f"{documento_id}.docx"
    storage = get_supabase().storage.from_(_DOCX_BUCKET)
    storage.upload(
        path=path,
        file=docx_bytes,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        },
    )
    return storage.get_public_url(path)


def _detect_headings(text: str) -> list[str]:
    """Detecta líneas que parecen headings en el texto de la plantilla."""
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if (
            3 <= len(stripped) <= 60
            and stripped[0].isupper()
            and not stripped.endswith((".", ",", ";", ":"))
            and " " in stripped
        ):
            headings.append(stripped)
    return headings[:10]


def run_documento(
    documento_id: str,
    archivos: list[tuple[str, bytes]],
    plantilla: tuple[str, bytes] | None,
    logo_bytes: bytes | None,
    titulo: str,
    secciones: list[str],
    indicaciones: str | None,
    opciones: dict,
) -> None:
    """
    Orquesta el pipeline completo de unificación de documentos.

    Ejecuta en orden: extracción de texto → detección de headings de plantilla →
    extracción de imágenes (si usar_imagenes) → build_documento_prompt →
    generate_documento_outline → generate_docx → Supabase Storage upload →
    DB update_resultado.

    Si cualquier paso falla, registra estado='error' en la DB y loguea con
    log.error. No relanza la excepción — el pipeline corre en background.

    Args:
        documento_id: UUID del documento ya insertado con estado='procesando'.
        archivos: Lista de (nombre, bytes) de los archivos fuente.
        plantilla: (nombre, bytes) de la plantilla DOCX base, o None.
        logo_bytes: Bytes del logo a insertar en la primera página, o None.
        titulo: Título del documento final.
        secciones: Secciones requeridas por el usuario.
        indicaciones: Indicaciones adicionales del usuario (puede ser None).
        opciones: Dict con homogeneizar, deduplicar, usar_imagenes.
    """
    try:
        textos_extraidos: dict[str, str] = {}
        for nombre, file_bytes in archivos:
            textos_extraidos[nombre] = extract_text_from_file(nombre, file_bytes)

        plantilla_secciones: list[str] | None = None
        plantilla_bytes: bytes | None = None
        if plantilla:
            plantilla_nombre, plantilla_bytes = plantilla
            try:
                texto_plantilla = extract_text_from_file(plantilla_nombre, plantilla_bytes)
                plantilla_secciones = _detect_headings(texto_plantilla)
            except AppError:
                pass  # plantilla sin texto útil — se ignoran sus secciones

        secciones = secciones if secciones else _DEFAULT_SECCIONES

        imagenes: list[tuple[str, bytes]] = []
        if opciones.get("usar_imagenes"):
            for nombre, file_bytes in archivos:
                for img_bytes in extract_images_from_file(nombre, file_bytes):
                    imagenes.append((nombre, img_bytes))

        prompt = build_documento_prompt(
            textos_extraidos, titulo, secciones,
            indicaciones, opciones, plantilla_secciones,
        )
        outline = generate_documento_outline(prompt)
        usar_imagenes = bool(opciones.get("usar_imagenes"))
        docx_bytes = generate_docx(outline, imagenes, usar_imagenes, plantilla_bytes, logo_bytes)
        docx_url = _upload_docx(documento_id, docx_bytes)
        documento_mutations_repo.update_resultado(documento_id, docx_url)
        log.info(f"documento.completed | id={documento_id}")

    except Exception as exc:
        documento_mutations_repo.update_error(documento_id)
        log.error(f"documento.failed | id={documento_id} | error={exc}")
