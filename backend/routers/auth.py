from fastapi import APIRouter, Depends, Request

from controllers.auth_controller import get_me, login, register
from middleware.auth import get_current_user
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register_endpoint(payload: RegisterRequest):
    return register(payload)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(payload: LoginRequest):
    return login(payload)


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: dict = Depends(get_current_user)):
    return get_me(current_user["sub"])
