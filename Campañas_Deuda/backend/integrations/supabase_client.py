"""
Wrapper del cliente de Supabase.

El service_key se usa para operaciones administrativas del backend (bypassea RLS).
La anon_key NO se usa desde el backend — es solo para el cliente frontend.

Por ahora este módulo no conecta a ninguna DB (ver CLAUDE.md §Estado de la DB).
El backend levanta sin conexión activa. Cuando se habilite la DB, será una sesión aparte.
"""

from config.settings import settings
from utils.errors import AppError
from utils.logger import logger

_client = None


def get_client():
    """
    Devuelve el cliente de Supabase inicializado con la service_key.

    El cliente se crea lazy (al primer uso) para que el backend levante
    sin una DB activa. Si las credenciales no están configuradas, lanza AppError.

    Returns:
        Cliente de Supabase.

    Raises:
        AppError: "DB_NOT_CONFIGURED" (503) si las variables de Supabase no están cargadas.
    """
    global _client
    if _client is not None:
        return _client

    if not settings.supabase_url or not settings.supabase_service_key:
        raise AppError(
            "Supabase no configurado — revisar SUPABASE_URL y SUPABASE_SERVICE_KEY",
            "DB_NOT_CONFIGURED",
            503,
        )

    # Stub: la importación y conexión real va en Sesión 3
    logger.info("Inicializando cliente Supabase (stub)")
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
