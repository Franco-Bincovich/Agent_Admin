from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from middleware.auth import register_auth_middleware
from middleware.error_handler import register_error_handlers
from routers import auth, documentos, generations, profile, users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="Agent Admin API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    register_auth_middleware(app)

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(generations.router, prefix="/api/v1/generations", tags=["generations"])
    app.include_router(documentos.router, prefix="/api/v1/documentos", tags=["documentos"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()
