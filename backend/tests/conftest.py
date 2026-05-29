import os

# Setear variables de entorno ANTES de cualquier import de la app.
# Esto garantiza que get_settings() use valores de test y no los del .env de desarrollo.
# JWT_SECRET debe tener al menos 32 caracteres (validador en Settings).
os.environ.update({
    "APP_ENV": "test",
    "ANTHROPIC_API_KEY": "sk-ant-test-key-for-tests",
    "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    "GAMMA_API_KEY": "test-gamma-api-key-for-tests",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_SERVICE_KEY": "test-service-key-not-real",
    "SUPABASE_ANON_KEY": "test-anon-key-not-real",
    "JWT_SECRET": "test-jwt-secret-at-least-32-chars-long!!",
    "JWT_EXPIRATION_MINUTES": "60",
    "REFRESH_TOKEN_EXPIRATION_DAYS": "30",
    "ALLOWED_ORIGINS": "http://localhost:3000",
})

# Rate limiting en tests: slowapi cuenta por IP en memoria y acumula entre tests
# (la suite dispara >20 POSTs de generación/min desde la misma IP de cliente),
# lo que dispararía 429 en tests no relacionados. Con el limiter ya centralizado
# en utils.limiter (una única instancia compartida por todos los routers), no se
# puede desactivar por-router sin apagar también el de auth. En su lugar se resetea
# el storage antes y después de cada test, de modo que cada test arranca limpio.
# test_rate_limit_login_returns_429 hace su propio reset/verificación encima de esto.
import pytest  # noqa: E402

from utils.limiter import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()
