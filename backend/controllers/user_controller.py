from repositories import user_mutations_repo, user_repo
from schemas.user import CreateUserRequest, UserResponse
from services.auth_service import hash_password
from utils.errors import AppError, ErrorCode


def create_user(payload: CreateUserRequest) -> UserResponse:
    """
    Crea un usuario nuevo desde el panel de administración.
    Verifica unicidad de email y username antes de insertar.

    Raises:
        AppError: USER_ALREADY_EXISTS 409 si el email o username ya existen.
    """
    if user_repo.find_by_email(payload.email):
        raise AppError("El email ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
    if user_repo.find_by_username(payload.username):
        raise AppError("El nombre de usuario ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
    user = user_mutations_repo.create_full(
        email=payload.email,
        nombre=payload.nombre,
        username=payload.username,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    return UserResponse(**user)


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
    is_admin = current_user.get("role") == "administrador"
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
    updated = user_mutations_repo.update_active(user_id, activo)
    return UserResponse(**updated)
