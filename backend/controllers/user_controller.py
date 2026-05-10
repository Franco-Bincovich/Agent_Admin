from schemas.user import CreateUserRequest, UserResponse
from services import user_service


def create_user(payload: CreateUserRequest) -> UserResponse:
    """Crea un usuario nuevo. Delega validación y creación a user_service."""
    return user_service.create_user(payload)


def get_all_users() -> list[UserResponse]:
    """Retorna todos los usuarios del sistema. Solo para administradores."""
    return user_service.get_all_users()


def get_user(user_id: str, current_user: dict) -> UserResponse:
    """Retorna el perfil de un usuario verificando ownership."""
    is_admin = current_user.get("role") == "administrador"
    return user_service.get_user(user_id, current_user["sub"], is_admin)


def update_user_active(user_id: str, activo: bool, requester: dict) -> UserResponse:
    """Activa o desactiva un usuario. Un admin no puede desactivarse a sí mismo."""
    return user_service.update_user_active(user_id, activo, requester["sub"])
