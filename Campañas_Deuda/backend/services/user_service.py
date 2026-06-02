from uuid import UUID

from schemas.user import UserCreate, UserResponse, UserUpdate
from utils.errors import AppError


async def list_users() -> list[UserResponse]:
    """
    Devuelve todos los usuarios del sistema.

    Solo debe ser invocado por un usuario con rol 'admin'.
    La verificación del rol se hace en el controller.

    Returns:
        Lista de UserResponse.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def create_user(request: UserCreate) -> UserResponse:
    """
    Crea un nuevo usuario hashando su contraseña.

    Args:
        request: Datos del nuevo usuario.

    Returns:
        UserResponse del usuario recién creado.

    Raises:
        AppError: "DUPLICATE_EMAIL" (409) si el email ya existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def update_user(user_id: UUID, request: UserUpdate) -> UserResponse:
    """
    Actualiza campos del usuario.

    Args:
        user_id: UUID del usuario.
        request: Campos a modificar (solo los no-None).

    Returns:
        UserResponse actualizado.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def deactivate_user(user_id: UUID) -> None:
    """
    Marca al usuario como inactivo (activo = False).

    No elimina el registro para preservar trazabilidad de ejecuciones.

    Args:
        user_id: UUID del usuario a desactivar.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 4.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
