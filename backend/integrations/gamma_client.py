from __future__ import annotations

import httpx

from config.settings import get_settings

GAMMA_BASE_URL = "https://public-api.gamma.app/v1.0"


def get_headers() -> dict:
    return {
        "X-API-KEY": get_settings().gamma_api_key,
        "Content-Type": "application/json",
    }


async def create_generation(payload: dict) -> dict:
    """
    Crea una generación en Gamma API v1.0.
    Retorna el dict con generationId.
    Raises: httpx.HTTPError si falla.
    """
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{GAMMA_BASE_URL}/generations",
            headers=get_headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def poll_generation(generation_id: str) -> dict:
    """
    Consulta el estado de una generación.
    Retorna el dict con status, gammaUrl, exportUrl.
    Raises: httpx.HTTPError si falla.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{GAMMA_BASE_URL}/generations/{generation_id}",
            headers=get_headers(),
        )
        response.raise_for_status()
        return response.json()
