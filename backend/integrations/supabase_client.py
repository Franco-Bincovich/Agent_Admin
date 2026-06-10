from __future__ import annotations

from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

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
        _client = _create_client()
    return _client


def recreate_supabase_client() -> Client:
    """
    Recrea el cliente descartando el singleton.

    Llamar tras un httpx.RemoteProtocolError: en Vercel serverless las
    conexiones keep-alive del cliente quedan muertas tras un freeze de la
    lambda, y el pool de httpx las reutiliza sin detectarlo.

    Returns:
        Cliente Supabase nuevo, ya asignado como singleton.
    """
    global _client
    _client = _create_client()
    return _client


def reset_supabase_client() -> None:
    """Forzar recreación del cliente en el próximo request. Útil en tests."""
    global _client
    _client = None


def _create_client() -> Client:
    """
    Crea un cliente Supabase con timeouts explícitos.

    supabase==2.7.4 no soporta pasar un transport httpx propio
    (ClientOptions no acepta httpx_client_options), por lo que la
    recuperación ante conexiones muertas se maneja con
    recreate_supabase_client() desde los callers.

    Returns:
        Cliente Supabase configurado.
    """
    settings = get_settings()
    options = ClientOptions(
        postgrest_client_timeout=15,
        storage_client_timeout=30,
    )
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
        options=options,
    )
