import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers import documento_controller
from middleware.auth import get_current_user
from schemas.documento import CreateDocumentoRequestV2, DocumentoResponse
from utils.errors import AppError, ErrorCode

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=DocumentoResponse, status_code=202)
@limiter.limit("20/minute")
async def create_documento(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: CreateDocumentoRequestV2,
    current_user: dict = Depends(get_current_user),
) -> DocumentoResponse:
    """
    Crea un nuevo documento DOCX y lo procesa en background.

    Raises:
        400: Formato de archivo no soportado o opciones inválidas (UNSUPPORTED_FORMAT / VALIDATION_ERROR)
        401: Token inválido o ausente (UNAUTHORIZED)
        429: Rate limit excedido (RATE_LIMIT_EXCEEDED)
    """
    try:
        secciones_list: list[str] = json.loads(payload.secciones)
    except json.JSONDecodeError:
        raise AppError("El campo secciones no es JSON válido", "INVALID_JSON", 400)
    return await documento_controller.create_documento(
        payload.titulo, secciones_list, payload.indicaciones, payload.opciones,
        payload.archivos_urls, payload.plantilla_url, payload.logo_url,
        background_tasks, current_user,
    )


@router.get("", response_model=list[DocumentoResponse])
def list_documentos(
    current_user: dict = Depends(get_current_user),
) -> list[DocumentoResponse]:
    """
    Retorna el historial de documentos del usuario autenticado.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
    """
    return documento_controller.get_documentos(current_user)


@router.get("/{documento_id}", response_model=DocumentoResponse)
def get_documento(
    documento_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> DocumentoResponse:
    """
    Retorna un documento por ID verificando ownership.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Documento no encontrado o sin acceso (NOT_FOUND)
    """
    return documento_controller.get_documento(str(documento_id), current_user)
