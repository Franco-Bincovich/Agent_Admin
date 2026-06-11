from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Única fuente de configuración del proyecto.
    Todos los módulos importan `settings` desde aquí — nunca os.environ directo.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # App
    app_env: str = "development"

    # Anthropic (Agentes)
    anthropic_api_key: str = ""

    # Perplexity (Agente Economista)
    perplexity_api_key: str = ""

    # Supabase — dejar vacío durante desarrollo sin DB
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    # Auth JWT
    jwt_secret: str = "dev-secret-reemplazar-en-produccion-min-32-chars"
    jwt_expiration_minutes: int = 60
    refresh_token_expiration_days: int = 30

    # CORS — lista separada por comas
    allowed_origins: str = "http://localhost:3000"

    # Gmail OAuth
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/api/auth/gmail/callback"

    # Payload máximo para uploads de cartera (10 MB)
    max_payload_bytes: int = 10 * 1024 * 1024


settings = Settings()
