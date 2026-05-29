from __future__ import annotations

from repositories import document_template_repo
from utils.errors import AppError, ErrorCode
from utils.logger import log


async def get_user_templates(usuario_id: str) -> list[dict]:
    """
    Devuelve todas las plantillas del usuario.

    Args:
        usuario_id: UUID del usuario propietario.

    Returns:
        Lista de plantillas ordenadas por creado_en desc (puede ser vacía).
    """
    return await document_template_repo.find_by_user(usuario_id)


async def get_template(template_id: str, usuario_id: str) -> dict:
    """
    Devuelve una plantilla por ID verificando ownership.

    Args:
        template_id: UUID de la plantilla.
        usuario_id: UUID del usuario solicitante.

    Returns:
        El registro de la plantilla.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    template = await document_template_repo.find_by_id(template_id, usuario_id)
    if template is None:
        raise AppError(
            f"Plantilla '{template_id}' no encontrada.",
            ErrorCode.NOT_FOUND,
            404,
        )
    return template


async def create_template(
    usuario_id: str,
    nombre: str,
    secciones: list[str],
) -> dict:
    """
    Crea una nueva plantilla de documento.

    Si es la primera plantilla del usuario, la marca automáticamente como default.

    Args:
        usuario_id: UUID del usuario propietario.
        nombre: Nombre de la plantilla (no puede ser vacío).
        secciones: Lista de identificadores de sección (no puede ser vacía).

    Returns:
        El registro completo de la plantilla creada.

    Raises:
        AppError: VALIDATION_ERROR 400 si nombre está vacío o secciones está vacía.
    """
    if not nombre or not nombre.strip():
        raise AppError("El nombre de la plantilla no puede estar vacío.", ErrorCode.VALIDATION_ERROR, 400)
    if not secciones:
        raise AppError("Las secciones no pueden estar vacías.", ErrorCode.VALIDATION_ERROR, 400)

    existing = await document_template_repo.find_by_user(usuario_id)
    is_default = len(existing) == 0

    template = await document_template_repo.create(
        usuario_id=usuario_id,
        nombre=nombre.strip(),
        secciones=secciones,
        is_default=is_default,
    )
    log.info(
        "document_template.created",
        extra={"template_id": template["id"], "usuario_id": usuario_id, "is_default": is_default},
    )
    return template


async def update_template(
    template_id: str,
    usuario_id: str,
    nombre: str,
    secciones: list[str],
    is_default: bool,
) -> dict:
    """
    Actualiza una plantilla existente verificando ownership.

    Args:
        template_id: UUID de la plantilla a actualizar.
        usuario_id: UUID del usuario propietario.
        nombre: Nuevo nombre (no puede ser vacío).
        secciones: Nueva lista de secciones (no puede ser vacía).
        is_default: Nuevo valor del flag de plantilla predeterminada.

    Returns:
        El registro actualizado.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
        AppError: VALIDATION_ERROR 400 si nombre está vacío o secciones está vacía.
    """
    if not nombre or not nombre.strip():
        raise AppError("El nombre de la plantilla no puede estar vacío.", ErrorCode.VALIDATION_ERROR, 400)
    if not secciones:
        raise AppError("Las secciones no pueden estar vacías.", ErrorCode.VALIDATION_ERROR, 400)

    updated = await document_template_repo.update(
        template_id=template_id,
        usuario_id=usuario_id,
        nombre=nombre.strip(),
        secciones=secciones,
        is_default=is_default,
    )
    if updated is None:
        raise AppError(
            f"Plantilla '{template_id}' no encontrada.",
            ErrorCode.NOT_FOUND,
            404,
        )
    log.info(
        "document_template.updated",
        extra={"template_id": template_id, "usuario_id": usuario_id},
    )
    return updated


async def delete_template(template_id: str, usuario_id: str) -> None:
    """
    Elimina una plantilla verificando ownership.

    Args:
        template_id: UUID de la plantilla a eliminar.
        usuario_id: UUID del usuario propietario.

    Returns:
        None.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    deleted = await document_template_repo.delete(template_id, usuario_id)
    if not deleted:
        raise AppError(
            f"Plantilla '{template_id}' no encontrada.",
            ErrorCode.NOT_FOUND,
            404,
        )
    log.info(
        "document_template.deleted",
        extra={"template_id": template_id, "usuario_id": usuario_id},
    )


async def set_default_template(template_id: str, usuario_id: str) -> dict:
    """
    Marca una plantilla como default, desmarcando las demás del usuario.

    Args:
        template_id: UUID de la plantilla que pasará a ser default.
        usuario_id: UUID del usuario propietario.

    Returns:
        El registro de la plantilla actualizada.

    Raises:
        AppError: NOT_FOUND 404 si no existe o no pertenece al usuario.
    """
    template = await document_template_repo.set_default(template_id, usuario_id)
    if template is None:
        raise AppError(
            f"Plantilla '{template_id}' no encontrada.",
            ErrorCode.NOT_FOUND,
            404,
        )
    log.info(
        "document_template.set_default",
        extra={"template_id": template_id, "usuario_id": usuario_id},
    )
    return template
