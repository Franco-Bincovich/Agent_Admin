from fastapi import APIRouter, Depends, Request

from controllers import profile_controller
from middleware.auth import get_current_user
from schemas.user import ChangePasswordRequest, ProfileResponse, UpdateProfileRequest
from utils.limiter import limiter

router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)) -> ProfileResponse:
    return await profile_controller.get_profile(current_user)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
) -> ProfileResponse:
    return await profile_controller.update_profile(payload, current_user)


@router.put("/password", status_code=200)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await profile_controller.change_password(payload, current_user)
