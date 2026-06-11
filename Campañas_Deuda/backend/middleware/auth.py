from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Rutas que no requieren token — lista explícita y corta (Principio de mínimo privilegio)
PUBLIC_ROUTES = [
    "/health",
    "/api/auth/register",
    "/api/auth/login",
    "/api/auth/refresh",
    "/docs",
    "/openapi.json",
    "/redoc",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación JWT.

    Stub — la implementación real (verificación de token, inyección de user en
    request.state) se completa en Sesión 3. Por ahora deja pasar todo para
    que el backend levante y /health responda sin dependencias externas.
    """

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        # TODO Sesión 3: extraer Bearer token, verificar JWT, inyectar user en request.state
        return await call_next(request)
