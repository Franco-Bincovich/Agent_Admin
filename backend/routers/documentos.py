import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers import documento_controller
from middleware.auth import get_current_user
from schemas.documento import DocumentoResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=DocumentoResponse, status_code=202)
@limiter.limit("20/minute")
async def create_documento(
    request: Request,
    background_tasks: BackgroundTasks,
    archivos: list[UploadFile] = File(...),
    titulo: str = Form(...),
    secciones: str = Form(default="[]"),
    indicaciones: Optional[str] = Form(default=None),
    opciones: str = Form(default="{}"),
    plantilla: Optional[UploadFile] = File(default=None),
    logo: Optional[UploadFile] = File(default=None),
    current_user: dict = Depends(get_current_user),
) -> DocumentoResponse:
    secciones_list: list[str] = json.loads(secciones)
    return await documento_controller.create_documento(
        titulo, secciones_list, indicaciones, opciones,
        archivos, plantilla, logo, background_tasks, current_user,
    )


@router.get("/", response_model=list[DocumentoResponse])
def list_documentos(
    current_user: dict = Depends(get_current_user),
) -> list[DocumentoResponse]:
    return documento_controller.get_documentos(current_user)


@router.get("/{documento_id}", response_model=DocumentoResponse)
def get_documento(
    documento_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> DocumentoResponse:
    return documento_controller.get_documento(str(documento_id), current_user)
