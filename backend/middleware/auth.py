from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.auth_service import verify_token
from utils.errors import AppError, ErrorCode

# Rutas que no requieren autenticación — la lista es explícita e intencionalmente corta
PUBLIC_ROUTES = [
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/docs",
    "/openapi.json",
]

_UNAUTHORIZED = {"error": True, "message": "No autorizado", "code": "UNAUTHORIZED"}


def register_auth_middleware(app: FastAPI) -> None:
    """Registra el middleware HTTP de autenticación JWT en la app FastAPI."""

    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        raw = request.headers.get("Authorization", "")
        header_token = raw.removeprefix("Bearer ").strip()
        token = header_token or request.cookies.get("access_token", "")
        if not token:
            return JSONResponse(status_code=401, content=_UNAUTHORIZED)

        try:
            payload = verify_token(token)
            if payload.get("type") != "access":
                raise ValueError("not an access token")
            request.state.user = payload
        except Exception:
            # Mensaje genérico — no revelar razón del rechazo (SEGURIDAD 2.3)
            return JSONResponse(status_code=401, content=_UNAUTHORIZED)

        return await call_next(request)


def get_current_user(request: Request) -> dict:
    """FastAPI dependency: retorna el payload JWT del request ya autenticado por el middleware."""
    return request.state.user


def require_admin(current_user: dict) -> None:
    """Verifica que el usuario tiene rol admin.
    Raises AppError FORBIDDEN 403 si no."""
    if current_user.get("role") != "administrador":
        raise AppError("No autorizado", ErrorCode.FORBIDDEN, 403)
