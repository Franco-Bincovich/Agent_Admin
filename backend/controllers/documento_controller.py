from __future__ import annotations

import json

from fastapi import BackgroundTasks, UploadFile

from repositories import documento_repo
from schemas.documento import DocumentoOpciones, DocumentoResponse
from services.documento_service import run_documento
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
    """
    Crea un documento con estado='procesando' y lanza el pipeline en background.

    Lee los bytes de cada archivo, valida y parsea las opciones, crea el registro
    en DB y agrega run_documento como BackgroundTask. Retorna DocumentoResponse
    inmediatamente sin esperar a que el pipeline termine.

    Args:
        titulo: Título del documento final.
        secciones: Lista de secciones requeridas (ya parseada desde JSON).
        indicaciones: Indicaciones adicionales del usuario (opcional).
        opciones_raw: JSON string con homogeneizar, deduplicar, usar_imagenes.
        archivos: Archivos fuente subidos (1 a 10).
        plantilla: Archivo .docx base para estilos (opcional).
        background_tasks: Objeto BackgroundTasks de FastAPI.
        current_user: Payload JWT del usuario autenticado.

    Returns:
        DocumentoResponse con estado='procesando', listo para retornar al cliente.
    """
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

    doc = documento_repo.create(
        current_user["sub"],
        titulo,
        [nombre for nombre, _ in archivos_data],
        plantilla_data[0] if plantilla_data else None,
        secciones,
        indicaciones,
        opciones,
    )

    background_tasks.add_task(
        run_documento,
        doc["id"], archivos_data, plantilla_data, logo_bytes,
        titulo, secciones, indicaciones, opciones,
    )
    return DocumentoResponse(**doc)


def get_documentos(current_user: dict) -> list[DocumentoResponse]:
    """Retorna el historial de documentos según el rol del usuario."""
    if current_user.get("rol") == "administrador":
        records = documento_repo.find_all()
    else:
        records = documento_repo.find_by_user(current_user["sub"])
    return [DocumentoResponse(**r) for r in records]


def get_documento(documento_id: str, current_user: dict) -> DocumentoResponse:
    """
    Retorna un documento verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).
    """
    doc = documento_repo.find_by_id(documento_id)
    if not doc:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    is_admin = current_user.get("rol") == "administrador"
    if not is_admin and doc["usuario_id"] != current_user["sub"]:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return DocumentoResponse(**doc)
