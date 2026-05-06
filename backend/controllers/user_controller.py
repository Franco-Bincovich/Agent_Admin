from repositories import user_repo
from schemas.user import UserResponse
from utils.errors import AppError, ErrorCode


def get_all_users() -> list[UserResponse]:
    """
    Retorna todos los usuarios del sistema.
    Solo debe invocarse desde endpoints de administrador.

    Returns:
        Lista de UserResponse con todos los usuarios, ordenados por creado_en DESC.
    """
    return [UserResponse(**u) for u in user_repo.find_all()]


def get_user(user_id: str, current_user: dict) -> UserResponse:
    """
    Retorna el perfil de un usuario verificando ownership.
    Editor y viewer solo pueden ver su propio perfil.
    Administrador puede ver cualquiera.
    Si el usuario no existe o el acceso no está permitido → 404, nunca 403 (SEGURIDAD 2.4).

    Args:
        user_id: UUID del usuario a consultar.
        current_user: Payload JWT del usuario autenticado.

    Returns:
        UserResponse con los datos del usuario.

    Raises:
        AppError: code NOT_FOUND (404) si el usuario no existe o no tiene acceso.
    """
    user = user_repo.find_by_id(user_id)
    if not user:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    is_admin = current_user.get("rol") == "administrador"
    if not is_admin and user["id"] != current_user["sub"]:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return UserResponse(**user)


def update_user_active(user_id: str, activo: bool, requester: dict) -> UserResponse:
    """
    Activa o desactiva un usuario. Solo debe invocarse para administradores.
    Un administrador no puede desactivarse a sí mismo.

    Args:
        user_id: UUID del usuario a modificar.
        activo: True para activar, False para desactivar.
        requester: Payload JWT del administrador que realiza la acción.

    Returns:
        UserResponse con los datos actualizados del usuario.

    Raises:
        AppError: code FORBIDDEN (403) si el administrador intenta desactivarse a sí mismo.
        AppError: code NOT_FOUND (404) si el usuario no existe.
    """
    if not activo and user_id == requester["sub"]:
        raise AppError(
            "Un administrador no puede desactivarse a sí mismo.",
            ErrorCode.FORBIDDEN,
            403,
        )
    updated = user_repo.update_active(user_id, activo)
    return UserResponse(**updated)
