from __future__ import annotations

import anthropic

from config.settings import get_settings

_client: anthropic.AsyncAnthropic | None = None


def get_anthropic_client() -> anthropic.AsyncAnthropic:
    """
    Retorna el cliente Anthropic asíncrono singleton, inicializado con la API key del entorno.

    La instancia se crea una única vez y se reutiliza en todas las llamadas
    para evitar overhead de inicialización en cada request.
    Es un cliente async (AsyncAnthropic): las llamadas deben hacerse con await
    para no bloquear el event loop. Timeout de 60s por request.
    No instanciar anthropic.AsyncAnthropic() directamente fuera de este módulo.

    Returns:
        Cliente AsyncAnthropic listo para usar.
    """
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(
            api_key=get_settings().anthropic_api_key,
            timeout=60.0,
        )
    return _client
