import anthropic

from config.settings import get_settings

_client: anthropic.Anthropic | None = None


def get_anthropic_client() -> anthropic.Anthropic:
    """
    Retorna el cliente Anthropic singleton, inicializado con la API key del entorno.

    La instancia se crea una única vez y se reutiliza en todas las llamadas
    para evitar overhead de inicialización en cada request.
    No instanciar anthropic.Anthropic() directamente fuera de este módulo.

    Returns:
        Cliente Anthropic listo para usar.
    """
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=get_settings().anthropic_api_key)
    return _client
