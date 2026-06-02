from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from middleware.auth import AuthMiddleware
from middleware.error_handler import global_error_handler
from middleware.security import PayloadLimitMiddleware, SecurityHeadersMiddleware
from routers import auth, executions, portfolio, users
from utils.logger import logger

app = FastAPI(
    title="Campañas de Deuda — API",
    description="Sistema interno de gestión de deuda asistido por IA — Municipalidad de Berazategui",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middlewares ─────────────────────────────────────────────────────────────
# Orden de add_middleware: el primero en la lista = más interno (se aplica al final).
# El último = más externo (envuelve todo, recibe el request primero).

# 1. CORS — el más interno, solo se aplica si el request supera auth y llega al handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 2. Auth (stub — implementación real en Sesión 3)
app.add_middleware(AuthMiddleware)

# 3. Límite de payload
app.add_middleware(PayloadLimitMiddleware)

# 4. Security headers — el más externo, agrega headers en todas las respuestas
app.add_middleware(SecurityHeadersMiddleware)

# ── Exception handler ────────────────────────────────────────────────────────
app.add_exception_handler(Exception, global_error_handler)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(executions.router, prefix="/api/executions", tags=["executions"])


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["infra"])
async def health_check() -> dict:
    """Endpoint público de liveness. No requiere autenticación."""
    logger.info("Health check")
    return {"status": "ok", "version": app.version, "env": settings.app_env}
