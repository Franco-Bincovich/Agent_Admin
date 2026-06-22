from schemas.user import CreateUserRequest, UserResponse
from services import user_admin_service, user_service


async def create_user(payload: CreateUserRequest) -> UserResponse:
    """Crea un usuario nuevo. Delega validación y creación a user_service."""
    return await user_service.create_user(payload)


async def get_all_users() -> list[UserResponse]:
    """Retorna todos los usuarios del sistema. Solo para administradores."""
    return await user_service.get_all_users()


async def get_user(user_id: str, current_user: dict) -> UserResponse:
    """Retorna el perfil de un usuario verificando ownership."""
    is_admin = current_user.get("role") == "administrador"
    return await user_service.get_user(user_id, current_user["sub"], is_admin)


async def update_user_active(user_id: str, activo: bool, requester: dict) -> UserResponse:
    """Activa o desactiva un usuario. Un admin no puede desactivarse a sí mismo."""
    return await user_admin_service.update_user_active(user_id, activo, requester["sub"])


async def update_user_role(user_id: str, rol: str, requester: dict) -> UserResponse:
    """Cambia el rol de un usuario. Un admin no puede cambiarse el rol a sí mismo."""
    return await user_admin_service.update_user_role(user_id, rol, requester["sub"])


async def update_user_manager(user_id: str, manager_id: str | None, requester: dict) -> UserResponse:
    """Asigna o desasigna el manager de un usuario líder. Delega al service admin."""
    return await user_admin_service.update_user_manager(user_id, manager_id, requester["sub"])


async def delete_user(user_id: str, current_user: dict) -> None:
    """Elimina un usuario permanentemente. Un admin no puede eliminarse a sí mismo."""
    await user_admin_service.delete_user(user_id, current_user["sub"])
