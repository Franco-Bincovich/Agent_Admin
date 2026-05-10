from __future__ import annotations

from repositories import documento_mutations_repo, documento_repo
from utils.errors import AppError, ErrorCode


def create_documento_record(
    usuario_id: str,
    titulo: str,
    archivos: list[str],
    plantilla_nombre: str | None,
    secciones: list[str],
    indicaciones: str | None,
    opciones: dict,
) -> dict:
    """
    Inserta un registro de documento con estado='procesando' en la DB.

    Args:
        usuario_id: UUID del usuario que inicia la generación.
        titulo: Título del documento final.
        archivos: Lista de nombres de los archivos fuente.
        plantilla_nombre: Nombre del archivo de plantilla DOCX base (puede ser None).
        secciones: Secciones requeridas por el usuario.
        indicaciones: Indicaciones adicionales (puede ser None).
        opciones: Dict con homogeneizar, deduplicar, usar_imagenes.

    Returns:
        Dict con los datos del registro creado, incluyendo el ID asignado.
    """
    return documento_mutations_repo.create(
        usuario_id, titulo, archivos, plantilla_nombre, secciones, indicaciones, opciones,
    )


def list_all_documentos() -> list[dict]:
    """Retorna todos los registros de documentos. Solo para administradores."""
    return documento_repo.find_all()


def list_user_documentos(user_id: str) -> list[dict]:
    """Retorna los registros de documentos del usuario indicado."""
    return documento_repo.find_by_user(user_id)


def get_documento_by_id(
    documento_id: str,
    user_id: str,
    is_admin: bool = False,
) -> dict:
    """
    Retorna un documento verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).

    Args:
        documento_id: UUID del documento a buscar.
        user_id: UUID del usuario autenticado (del JWT).
        is_admin: True si el usuario tiene rol administrador.

    Returns:
        Dict con los datos del documento.

    Raises:
        AppError: code NOT_FOUND (404) si no existe o el usuario no tiene acceso.
    """
    doc = documento_repo.find_by_id(documento_id)
    if not doc:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    if not is_admin and doc["usuario_id"] != user_id:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return doc
