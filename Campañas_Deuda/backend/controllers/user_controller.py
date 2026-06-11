from uuid import UUID

from schemas.user import UserCreate, UserResponse, UserUpdate
from utils.errors import AppError


async def list_users() -> list[UserResponse]:
    """
    Lista todos los usuarios del sistema (solo admin).

    Returns:
        Lista de UserResponse.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def create_user(request: UserCreate) -> UserResponse:
    """
    Crea un usuario nuevo (solo admin).

    Args:
        request: Datos del nuevo usuario.

    Returns:
        UserResponse del usuario creado.

    Raises:
        AppError: "DUPLICATE_EMAIL" (409) si el email ya existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def update_user(user_id: UUID, request: UserUpdate) -> UserResponse:
    """
    Actualiza nombre, estado o rol de un usuario (solo admin).

    Args:
        user_id: UUID del usuario a actualizar.
        request: Campos a actualizar.

    Returns:
        UserResponse actualizado.

    Raises:
        AppError: "NOT_FOUND" (404) si el usuario no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def deactivate_user(user_id: UUID) -> None:
    """
    Desactiva un usuario (soft delete — no borra de la DB).

    Args:
        user_id: UUID del usuario a desactivar.

    Raises:
        AppError: "NOT_FOUND" (404) si el usuario no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
