from fastapi import APIRouter, Depends, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers.auth_controller import get_me, login, register
from controllers.token_controller import logout, refresh_tokens
from middleware.auth import get_current_user
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from schemas.auth import TokenResponse as _TokenResponse
from schemas.user import UserResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_ACCESS_MAX_AGE = 3600
_REFRESH_MAX_AGE = 60 * 60 * 24 * 30


def _set_auth_cookies(response: Response, tokens: _TokenResponse) -> None:
    response.set_cookie(
        key="access_token", value=tokens.access_token,
        httponly=True, secure=True, samesite="lax", max_age=_ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token", value=tokens.refresh_token,
        httponly=True, secure=True, samesite="lax", max_age=_REFRESH_MAX_AGE,
    )


@router.post("/register", status_code=201)
async def register_endpoint(payload: RegisterRequest, response: Response):
    _set_auth_cookies(response, register(payload))
    return {"ok": True}


@router.post("/login")
@limiter.limit("5/minute")
async def login_endpoint(request: Request, payload: LoginRequest, response: Response):
    _set_auth_cookies(response, login(payload, request))
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: dict = Depends(get_current_user)):
    return get_me(current_user["sub"])


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_endpoint(request: Request, payload: RefreshRequest, response: Response):
    _set_auth_cookies(response, refresh_tokens(payload))
    return {"ok": True}


@router.post("/logout", status_code=200)
async def logout_endpoint(response: Response, current_user: dict = Depends(get_current_user)):
    result = logout(current_user["sub"])
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")
    return result
