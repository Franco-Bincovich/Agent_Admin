from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi import Response

import controllers.document_template_controller as controller
from middleware.auth import get_current_user
from schemas.document_template import (
    CreateTemplateRequest,
    TemplateResponse,
    UpdateTemplateRequest,
)
from utils.limiter import limiter

router = APIRouter(prefix="/api/v1/document-templates", tags=["document-templates"])


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    current_user: dict = Depends(get_current_user),
) -> list[TemplateResponse]:
    """
    Retorna todas las plantillas del usuario autenticado.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
    """
    return await controller.list_templates(current_user["sub"])


@router.post("", response_model=TemplateResponse, status_code=201)
@limiter.limit("20/minute")
async def create_template(
    request: Request,
    payload: CreateTemplateRequest,
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """
    Crea una nueva plantilla de documento.

    Raises:
        400: Nombre vacío o secciones vacías (VALIDATION_ERROR)
        401: Token inválido o ausente (UNAUTHORIZED)
        429: Rate limit excedido (RATE_LIMIT_EXCEEDED)
    """
    return await controller.create_template(payload, current_user["sub"])


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """
    Retorna una plantilla por ID verificando ownership.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Plantilla no encontrada o sin acceso (NOT_FOUND)
    """
    return await controller.get_template(str(template_id), current_user["sub"])


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    payload: UpdateTemplateRequest,
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """
    Actualiza una plantilla existente verificando ownership.

    Raises:
        400: Nombre vacío o secciones vacías (VALIDATION_ERROR)
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Plantilla no encontrada o sin acceso (NOT_FOUND)
    """
    return await controller.update_template(str(template_id), payload, current_user["sub"])


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """
    Elimina una plantilla verificando ownership.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Plantilla no encontrada o sin acceso (NOT_FOUND)
    """
    await controller.delete_template(str(template_id), current_user["sub"])
    return Response(status_code=204)


@router.patch("/{template_id}/default", response_model=TemplateResponse)
async def set_default_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """
    Marca una plantilla como default, desmarcando las demás del usuario.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Plantilla no encontrada o sin acceso (NOT_FOUND)
    """
    return await controller.set_default_template(str(template_id), current_user["sub"])
