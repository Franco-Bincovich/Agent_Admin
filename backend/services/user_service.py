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
