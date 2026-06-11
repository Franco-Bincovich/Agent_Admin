from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from config.settings import get_settings
from middleware.auth import register_auth_middleware
from middleware.error_handler import register_error_handlers
from routers import activity, auth, document_templates, documentos, generations, planificacion, profile, users, video
from utils.limiter import limiter
from utils.logger import log
from repositories import generation_repo, documento_repo, documento_mutations_repo, planificacion_repo

settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if "server" in response.headers:
            del response.headers["server"]
        return response


MAX_PAYLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


async def _reap_stalled() -> None:
    """Marca como error los registros procesando por más de 30 minutos."""
    try:
        stalled_gens = await generation_repo.find_stalled(older_than_minutes=30)
        for gen in (stalled_gens.data or []):
            await generation_repo.update_error(gen["id"])
            log.warning(
                "Generación colgada marcada como error",
                extra={"generation_id": gen["id"]}
            )

        stalled_docs = await documento_repo.find_stalled(older_than_minutes=30)
        for doc in (stalled_docs.data or []):
            await documento_mutations_repo.update_error(doc["id"])
            log.warning(
                "Documento colgado marcado como error",
                extra={"documento_id": doc["id"]}
            )
        stalled_plans = await planificacion_repo.find_stalled(older_than_minutes=30)
        for plan in (stalled_plans.data or []):
            await planificacion_repo.update_error(plan["id"])
            log.warning(
                "Planificación colgada marcada como error",
                extra={"proyecto_id": plan["id"]}
            )
    except Exception as e:
        log.error("Error en reaper", extra={"error": str(e)})


async def _reaper_loop() -> None:
    """Corre el reaper cada 10 minutos."""
    while True:
        await asyncio.sleep(600)
        await _reap_stalled()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: lanzar reaper en background
    reaper_task = asyncio.create_task(_reaper_loop())
    yield
    # Shutdown: cancelar reaper limpiamente
    reaper_task.cancel()
    try:
        await reaper_task
    except asyncio.CancelledError:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="Agent Admin API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
        redirect_slashes=True,
    )

    @app.middleware("http")
    async def limit_payload_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "error": True,
                    "message": "Payload demasiado grande",
                    "code": "PAYLOAD_TOO_LARGE",
                },
            )
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_middleware(SecurityHeadersMiddleware)

    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": True,
                "message": "Demasiadas solicitudes. Intentá de nuevo en un momento.",
                "code": "RATE_LIMIT_EXCEEDED",
            },
            headers={"Retry-After": "60"},
        )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    register_error_handlers(app)
    register_auth_middleware(app)

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(generations.router, prefix="/api/v1/generations", tags=["generations"])
    app.include_router(documentos.router, prefix="/api/v1/documentos", tags=["documentos"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
    app.include_router(activity.router, prefix="/api/v1/activity", tags=["activity"])
    app.include_router(video.router, prefix="/api/v1/video", tags=["video"])
    app.include_router(document_templates.router)
    app.include_router(planificacion.router, prefix="/api/v1/planificacion", tags=["planificacion"])

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
