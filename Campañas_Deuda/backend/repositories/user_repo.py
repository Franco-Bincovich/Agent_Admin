from uuid import UUID

from schemas.user import UserResponse
from utils.errors import AppError


async def find_by_email(email: str) -> UserResponse | None:
    """
    Busca un usuario por email. Devuelve None si no existe.

    Args:
        email: Email del usuario.

    Returns:
        UserResponse o None.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def find_by_id(user_id: UUID) -> UserResponse | None:
    """
    Busca un usuario por UUID. Devuelve None si no existe.

    Args:
        user_id: UUID del usuario.

    Returns:
        UserResponse o None.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def save(user_data: dict) -> UserResponse:
    """
    Persiste un usuario nuevo en la DB.

    Args:
        user_data: Dict con todos los campos del usuario (password ya hasheada).

    Returns:
        UserResponse del usuario creado.

    Raises:
        AppError: "DUPLICATE_EMAIL" (409) si viola la constraint unique.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def update(user_id: UUID, fields: dict) -> UserResponse:
    """
    Actualiza campos de un usuario existente.

    Args:
        user_id: UUID del usuario.
        fields: Diccionario con solo los campos a actualizar.

    Returns:
        UserResponse actualizado.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
