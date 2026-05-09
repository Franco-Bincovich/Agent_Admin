from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from controllers import user_controller
from middleware.auth import get_current_user
from schemas.user import CreateUserRequest, UserResponse
from utils.errors import AppError, ErrorCode

router = APIRouter()


class ActivePayload(BaseModel):
    activo: bool


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: CreateUserRequest,
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    if current_user.get("role") != "administrador":
        raise AppError("Acceso denegado", ErrorCode.FORBIDDEN, 403)
    return user_controller.create_user(payload)


@router.get("", response_model=list[UserResponse])
def list_users(
    current_user: dict = Depends(get_current_user),
) -> list[UserResponse]:
    if current_user.get("role") != "administrador":
        raise AppError("Acceso denegado", ErrorCode.FORBIDDEN, 403)
    return user_controller.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    return user_controller.get_user(str(user_id), current_user)


@router.patch("/{user_id}/active", response_model=UserResponse)
def update_active(
    user_id: UUID,
    payload: ActivePayload,
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    if current_user.get("role") != "administrador":
        raise AppError("Acceso denegado", ErrorCode.FORBIDDEN, 403)
    return user_controller.update_user_active(str(user_id), payload.activo, current_user)
