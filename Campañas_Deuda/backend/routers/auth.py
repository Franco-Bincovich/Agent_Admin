from fastapi import APIRouter

from controllers import auth_controller
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest) -> TokenResponse:
    """Registro de nuevo usuario. Stub — implementar en Sesión 3."""
    return await auth_controller.register_user(body)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    """Login con email y contraseña. Stub — implementar en Sesión 3."""
    return await auth_controller.login_user(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest) -> TokenResponse:
    """Rotación de refresh token. Stub — implementar en Sesión 3."""
    return await auth_controller.refresh_tokens(body)


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest) -> None:
    """Invalidar refresh token. Stub — implementar en Sesión 3."""
    await auth_controller.logout_user(body)
