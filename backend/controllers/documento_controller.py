from __future__ import annotations

import json
from urllib.parse import unquote, urlparse

from fastapi import BackgroundTasks

from schemas.documento import DocumentoOpciones, DocumentoResponse
from services.documento_record_service import (
    create_documento_record,
    get_documento_by_id,
    list_all_documentos,
    list_user_documentos,
)
from services.documento_service import run_document_generation
from utils.errors import AppError, ErrorCode


def _filename_from_url(url: str) -> str:
    path = urlparse(url).path
    return unquote(path.rsplit("/", 1)[-1]) or "archivo"


async def create_documento(
    titulo: str,
    secciones: list[str],
    indicaciones: str | None,
    opciones_raw: str,
    archivos_urls: list[str],
    plantilla_url: str | None,
    logo_url: str | None,
    background_tasks: BackgroundTasks,
    current_user: dict,
) -> DocumentoResponse:
    try:
        opciones = DocumentoOpciones(**json.loads(opciones_raw)).model_dump()
    except Exception:
        raise AppError("Opciones inválidas.", ErrorCode.VALIDATION_ERROR, 400)

    archivos_nombres = [_filename_from_url(u) for u in archivos_urls]
    plantilla_nombre = _filename_from_url(plantilla_url) if plantilla_url else None

    doc = create_documento_record(
        current_user["sub"],
        titulo,
        archivos_nombres,
        plantilla_nombre,
        secciones,
        indicaciones,
        opciones,
    )

    background_tasks.add_task(
        run_document_generation,
        doc["id"], archivos_urls, plantilla_url, logo_url,
        titulo, secciones, indicaciones, opciones,
    )
    return DocumentoResponse(**doc)


def get_documentos(current_user: dict) -> list[DocumentoResponse]:
    """Retorna el historial de documentos según el rol del usuario."""
    if current_user.get("role") == "administrador":
        records = list_all_documentos()
    else:
        records = list_user_documentos(current_user["sub"])
    return [DocumentoResponse(**r) for r in records]


def get_documento(documento_id: str, current_user: dict) -> DocumentoResponse:
    """
    Retorna un documento verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).
    """
    is_admin = current_user.get("role") == "administrador"
    doc = get_documento_by_id(documento_id, current_user["sub"], is_admin)
    return DocumentoResponse(**doc)
