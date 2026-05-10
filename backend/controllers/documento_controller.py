from __future__ import annotations

import json

from fastapi import BackgroundTasks, UploadFile

from schemas.documento import DocumentoOpciones, DocumentoResponse
from services.documento_record_service import (
    create_documento_record,
    get_documento_by_id,
    list_all_documentos,
    list_user_documentos,
)
from services.documento_service import run_document_generation
from utils.errors import AppError, ErrorCode


async def create_documento(
    titulo: str,
    secciones: list[str],
    indicaciones: str | None,
    opciones_raw: str,
    archivos: list[UploadFile],
    plantilla: UploadFile | None,
    logo: UploadFile | None,
    background_tasks: BackgroundTasks,
    current_user: dict,
) -> DocumentoResponse:
    try:
        opciones = DocumentoOpciones(**json.loads(opciones_raw)).model_dump()
    except Exception:
        raise AppError("Opciones inválidas.", ErrorCode.VALIDATION_ERROR, 400)

    archivos_data: list[tuple[str, bytes]] = []
    for archivo in archivos:
        contenido = await archivo.read()
        archivos_data.append((archivo.filename or "archivo", contenido))

    plantilla_data: tuple[str, bytes] | None = None
    if plantilla:
        plantilla_bytes = await plantilla.read()
        plantilla_data = (plantilla.filename or "plantilla.docx", plantilla_bytes)

    logo_bytes: bytes | None = None
    if logo:
        logo_bytes = await logo.read()

    doc = create_documento_record(
        current_user["sub"],
        titulo,
        [nombre for nombre, _ in archivos_data],
        plantilla_data[0] if plantilla_data else None,
        secciones,
        indicaciones,
        opciones,
    )

    background_tasks.add_task(
        run_document_generation,
        doc["id"], archivos_data, plantilla_data, logo_bytes,
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
