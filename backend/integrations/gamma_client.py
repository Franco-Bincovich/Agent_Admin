import httpx
from config.settings import get_settings

# Cliente HTTP para la Gamma API. Usar get_gamma_client() para obtener la sesión.
# Base URL y auth headers se configuran aquí; no hardcodear en gamma_service.


def get_gamma_client() -> httpx.AsyncClient:
    """Retorna un cliente HTTP configurado para la Gamma API."""
    settings = get_settings()
    return httpx.AsyncClient(
        base_url="https://api.gamma.app",
        headers={"Authorization": f"Bearer {settings.gamma_api_key}"},
        timeout=30.0,
    )
