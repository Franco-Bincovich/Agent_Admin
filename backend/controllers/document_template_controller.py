from __future__ import annotations

from schemas.document_template import (
    CreateTemplateRequest,
    TemplateResponse,
    UpdateTemplateRequest,
)
from services import document_template_service


async def list_templates(usuario_id: str) -> list[TemplateResponse]:
    """Retorna todas las plantillas del usuario."""
    records = await document_template_service.get_user_templates(usuario_id)
    return [TemplateResponse.from_db(r) for r in records]


async def get_template(template_id: str, usuario_id: str) -> TemplateResponse:
    """
    Retorna una plantilla por ID verificando ownership.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    record = await document_template_service.get_template(template_id, usuario_id)
    return TemplateResponse.from_db(record)


async def create_template(
    payload: CreateTemplateRequest,
    usuario_id: str,
) -> TemplateResponse:
    """
    Crea una nueva plantilla.

    Raises:
        AppError: VALIDATION_ERROR 400 si nombre vacío o secciones vacías.
    """
    record = await document_template_service.create_template(
        usuario_id=usuario_id,
        nombre=payload.nombre,
        secciones=payload.secciones,
    )
    return TemplateResponse.from_db(record)


async def update_template(
    template_id: str,
    payload: UpdateTemplateRequest,
    usuario_id: str,
) -> TemplateResponse:
    """
    Actualiza una plantilla existente.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
        AppError: VALIDATION_ERROR 400 si nombre vacío o secciones vacías.
    """
    record = await document_template_service.update_template(
        template_id=template_id,
        usuario_id=usuario_id,
        nombre=payload.nombre,
        secciones=payload.secciones,
        is_default=payload.is_default,
    )
    return TemplateResponse.from_db(record)


async def delete_template(template_id: str, usuario_id: str) -> None:
    """
    Elimina una plantilla.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    await document_template_service.delete_template(template_id, usuario_id)


async def set_default_template(template_id: str, usuario_id: str) -> TemplateResponse:
    """
    Marca una plantilla como default.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    record = await document_template_service.set_default_template(template_id, usuario_id)
    return TemplateResponse.from_db(record)
