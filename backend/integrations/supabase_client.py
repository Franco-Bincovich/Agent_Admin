from __future__ import annotations

from supabase import Client, create_client

from config.settings import get_settings

_client: Client | None = None


def get_supabase() -> Client:
    """
    Retorna el cliente Supabase singleton inicializado con service_key.

    Usa service_key (acceso administrativo completo, bypasea RLS).
    Solo debe usarse en el backend — nunca exponer al frontend (SEGURIDAD 4.3).
    La instancia se crea una única vez y se reutiliza en todas las llamadas.

    Returns:
        Cliente Supabase listo para usar.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client
