from __future__ import annotations

import httpx

from config.settings import get_settings


def get_gamma_client() -> httpx.AsyncClient:
    """Retorna un cliente HTTP async configurado para la Gamma API."""
    settings = get_settings()
    return httpx.AsyncClient(
        base_url="https://api.gamma.app",
        headers={"Authorization": f"Bearer {settings.gamma_api_key}"},
        timeout=60.0,
    )
