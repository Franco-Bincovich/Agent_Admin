from uuid import UUID

from fastapi import APIRouter

from controllers import user_controller
from schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """Listar todos los usuarios (solo admin). Stub — implementar en Sesión 4."""
    return await user_controller.list_users()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(body: UserCreate) -> UserResponse:
    """Crear usuario (solo admin). Stub — implementar en Sesión 4."""
    return await user_controller.create_user(body)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, body: UserUpdate) -> UserResponse:
    """Actualizar usuario (solo admin). Stub — implementar en Sesión 4."""
    return await user_controller.update_user(user_id, body)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: UUID) -> None:
    """Desactivar usuario (solo admin). Stub — implementar en Sesión 4."""
    await user_controller.deactivate_user(user_id)
