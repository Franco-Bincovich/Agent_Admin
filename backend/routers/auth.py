from fastapi import APIRouter, Depends, Request, Response

from controllers.auth_controller import get_me, login
from controllers.token_controller import logout, refresh_tokens
from middleware.auth import get_current_user
from schemas.auth import LoginRequest
from utils.errors import AppError
from utils.limiter import limiter
from schemas.auth import TokenResponse as _TokenResponse
from schemas.user import UserResponse

router = APIRouter()

_ACCESS_MAX_AGE = 3600
_REFRESH_MAX_AGE = 60 * 60 * 24 * 30


def _set_auth_cookies(response: Response, tokens: _TokenResponse) -> None:
    response.set_cookie(
        key="access_token", value=tokens.access_token,
        httponly=True, secure=True, samesite="none", max_age=_ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token", value=tokens.refresh_token,
        httponly=True, secure=True, samesite="none", max_age=_REFRESH_MAX_AGE,
    )


@router.post("/login")
@limiter.limit("5/minute")
async def login_endpoint(request: Request, payload: LoginRequest, response: Response):
    _set_auth_cookies(response, await login(payload))
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: dict = Depends(get_current_user)):
    return await get_me(current_user["sub"])


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_endpoint(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AppError("Refresh token no encontrado", "UNAUTHORIZED", 401)
    _set_auth_cookies(response, await refresh_tokens(refresh_token))
    return {"ok": True}


@router.post("/logout", status_code=200)
async def logout_endpoint(response: Response, current_user: dict = Depends(get_current_user)):
    result = await logout(current_user["sub"])
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="none")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="none")
    return result
