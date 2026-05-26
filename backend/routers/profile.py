from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers import profile_controller
from middleware.auth import get_current_user
from schemas.user import ChangePasswordRequest, ProfileResponse, UpdateProfileRequest

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)) -> ProfileResponse:
    return profile_controller.get_profile(current_user)


@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
) -> ProfileResponse:
    return profile_controller.update_profile(payload, current_user)


@router.put("/password", status_code=200)
@limiter.limit("5/minute")
def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return profile_controller.change_password(payload, current_user)
