from fastapi import Request
from fastapi.responses import JSONResponse

from utils.errors import AppError
from utils.logger import logger


async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler global de excepciones.

    Captura AppError y cualquier excepción inesperada. Siempre devuelve
    el mismo formato: { "error": true, "message": ..., "code": ... }.
    Los errores inesperados se loguean con stack trace pero no exponen
    detalles internos al cliente.
    """
    if isinstance(exc, AppError):
        logger.warning(
            exc.message,
            extra={"code": exc.code, "path": str(request.url.path)},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": exc.message, "code": exc.code},
        )

    logger.error(
        "Error inesperado",
        extra={"error": str(exc), "path": str(request.url.path), "type": type(exc).__name__},
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "code": "INTERNAL_ERROR",
        },
    )
