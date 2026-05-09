from fastapi import APIRouter, Depends

from controllers import profile_controller
from middleware.auth import get_current_user
from schemas.user import ChangePasswordRequest, ProfileResponse, UpdateProfileRequest

router = APIRouter()


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
def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return profile_controller.change_password(payload, current_user)
