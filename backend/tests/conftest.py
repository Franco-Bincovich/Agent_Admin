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
    "ALLOWED_ORIGINS": '["http://localhost:3000"]',
})
