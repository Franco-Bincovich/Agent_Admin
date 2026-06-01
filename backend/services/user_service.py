import asyncio

from repositories import user_mutations_repo, user_repo
from repositories.generation_repo import find_by_user as find_generaciones
from repositories.documento_repo import find_by_user as find_documentos
from schemas.user import CreateUserRequest, UserResponse
from services.auth_service import hash_password
from utils.errors import AppError, ErrorCode


async def create_user(payload: CreateUserRequest) -> UserResponse:
    """
    Crea un usuario nuevo desde el panel de administración.
    Verifica unicidad de email y username antes de insertar.

    Args:
        payload: Datos del nuevo usuario validados por Pydantic.

    Returns:
        UserResponse con los datos del usuario creado.

    Raises:
        AppError: USER_ALREADY_EXISTS 409 si el email o username ya existen.
    """
    if await user_repo.find_by_email(payload.email):
        raise AppError("El email ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
    if await user_repo.find_by_username(payload.username):
        raise AppError("El nombre de usuario ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
    user = await user_mutations_repo.create_full(
        email=payload.email,
        nombre=payload.nombre,
        username=payload.username,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    return UserResponse(**user)


async def get_all_users() -> list[UserResponse]:
    """
    Retorna todos los usuarios del sistema con su conteo de generaciones.
    Solo debe invocarse desde endpoints de administrador.

    Returns:
        Lista de UserResponse con todos los usuarios, ordenados por creado_en DESC.
        Cada usuario incluye total_generaciones (presentaciones + documentos).
    """
    users = await user_repo.find_all()
    result = []
    for u in users:
        gen, doc = await asyncio.gather(
            find_generaciones(u["id"], limit=9999),
            find_documentos(u["id"], limit=9999),
        )
        result.append(UserResponse(**u, total_generaciones=len(gen) + len(doc)))
    return result


async def get_user(user_id: str, requester_id: str, is_admin: bool = False) -> UserResponse:
    """
    Retorna el perfil de un usuario verificando ownership.
    Editor y viewer solo pueden ver su propio perfil.
    Si el usuario no existe o el acceso no está permitido → 404, nunca 403 (SEGURIDAD 2.4).

    Args:
        user_id: UUID del usuario a consultar.
        requester_id: UUID del usuario autenticado (del JWT).
        is_admin: True si el usuario tiene rol administrador.

    Returns:
        UserResponse con los datos del usuario.

    Raises:
        AppError: code NOT_FOUND (404) si el usuario no existe o no tiene acceso.
    """
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    if not is_admin and user["id"] != requester_id:
        raise AppError("No encontrado", ErrorCode.NOT_FOUND, 404)
    return UserResponse(**user)


async def update_user_active(user_id: str, activo: bool, requester_id: str) -> UserResponse:
    """
    Activa o desactiva un usuario. Solo debe invocarse para administradores.
    Un administrador no puede desactivarse a sí mismo.

    Args:
        user_id: UUID del usuario a modificar.
        activo: True para activar, False para desactivar.
        requester_id: UUID del administrador que realiza la acción.

    Returns:
        UserResponse con los datos actualizados del usuario.

    Raises:
        AppError: code FORBIDDEN (403) si el administrador intenta desactivarse a sí mismo.
        AppError: code NOT_FOUND (404) si el usuario no existe.
    """
    if not activo and user_id == requester_id:
        raise AppError(
            "Un administrador no puede desactivarse a sí mismo.",
            ErrorCode.FORBIDDEN,
            403,
        )
    updated = await user_mutations_repo.update_active(user_id, activo)
    return UserResponse(**updated)


async def delete_user(user_id: str, requester_id: str) -> None:
    """
    Elimina un usuario permanentemente (hard delete).
    No permite que un admin se elimine a sí mismo.

    Args:
        user_id: ID del usuario a eliminar.
        requester_id: ID del admin que ejecuta la acción.

    Raises:
        AppError FORBIDDEN 403 si intenta eliminarse a sí mismo.
        AppError NOT_FOUND 404 si el usuario no existe.
    """
    if user_id == requester_id:
        raise AppError("No podés eliminar tu propia cuenta", ErrorCode.FORBIDDEN, 403)
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise AppError("Usuario no encontrado", ErrorCode.NOT_FOUND, 404)
    await user_mutations_repo.delete(user_id)
