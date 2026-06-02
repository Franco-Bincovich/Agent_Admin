from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Agrega headers de seguridad HTTP a todas las respuestas."""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # No exponer el framework al cliente
        if "server" in response.headers:
            del response.headers["server"]
        return response


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    """Rechaza payloads que superen el límite configurado en settings."""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_payload_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "error": True,
                    "message": "El archivo supera el tamaño máximo permitido",
                    "code": "PAYLOAD_TOO_LARGE",
                },
            )
        return await call_next(request)
