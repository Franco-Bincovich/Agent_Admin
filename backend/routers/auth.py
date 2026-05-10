from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers.auth_controller import get_me, login, register
from controllers.token_controller import logout, refresh_tokens
from middleware.auth import get_current_user
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register_endpoint(payload: RegisterRequest):
    return register(payload)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login_endpoint(request: Request, payload: LoginRequest):
    return login(payload)


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: dict = Depends(get_current_user)):
    return get_me(current_user["sub"])


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_endpoint(request: Request, payload: RefreshRequest):
    return refresh_tokens(payload)


@router.post("/logout", status_code=200)
async def logout_endpoint(current_user: dict = Depends(get_current_user)):
    return logout(current_user["sub"])
