from __future__ import annotations

from repositories import generation_repo
from utils.errors import AppError, ErrorCode


def create_generation_record(
    user_id: str,
    objetivo: str,
    filenames: list[str],
    parametros: dict,
) -> dict:
    """
    Inserta un registro de generación con estado='procesando' en la DB.

    Args:
        user_id: UUID del usuario que inicia la generación.
        objetivo: Objetivo declarado de la presentación.
        filenames: Lista de nombres de los archivos fuente.
        parametros: Dict con los parámetros de generación (template, tono, etc.).

    Returns:
        Dict con los datos del registro creado, incluyendo el ID asignado.
    """
    return generation_repo.create(user_id, objetivo, filenames, parametros)


def list_all_generations() -> list[dict]:
    """Retorna todos los registros de generación. Solo para administradores."""
    return generation_repo.find_all()


def list_user_generations(user_id: str) -> list[dict]:
    """Retorna los registros de generación del usuario indicado."""
    return generation_repo.find_by_user(user_id)


def get_generation_by_id(
    generation_id: str,
    user_id: str,
    is_admin: bool = False,
) -> dict:
    """
    Retorna una generación verificando ownership. Devuelve 404 si no existe
    o si el usuario no es propietario — nunca 403 (SEGURIDAD 2.4).

    Args:
        generation_id: UUID de la generación a buscar.
        user_id: UUID del usuario autenticado (del JWT).
        is_admin: True si el usuario tiene rol administrador.

    Returns:
        Dict con los datos de la generación.

    Raises:
        AppError: code NOT_FOUND (404) si no existe o el usuario no tiene acceso.
    """
    gen = generation_repo.find_by_id(generation_id)
    if not gen:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    if not is_admin and gen["usuario_id"] != user_id:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return gen
