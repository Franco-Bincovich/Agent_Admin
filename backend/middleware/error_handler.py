from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from utils.errors import AppError
from utils.logger import log


async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log.warning(f"app_error | path={request.url.path} code={exc.code} msg={exc.message}")
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error(f"unhandled_error | path={request.url.path} error={exc!r}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Error interno del servidor.", "code": "INTERNAL_ERROR"},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de errores en la app FastAPI."""
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
