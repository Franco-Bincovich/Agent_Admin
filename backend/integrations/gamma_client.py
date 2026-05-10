from __future__ import annotations

import httpx
from config.settings import get_settings
from utils.logger import log

# Cliente HTTP para la Gamma API. Usar get_gamma_client() para obtener la sesión.
# Base URL y auth headers se configuran aquí; no hardcodear en gamma_service.


def get_gamma_client() -> httpx.AsyncClient:
    """Retorna un cliente HTTP async configurado para la Gamma API."""
    settings = get_settings()
    return httpx.AsyncClient(
        base_url="https://api.gamma.app",
        headers={"Authorization": f"Bearer {settings.gamma_api_key}"},
        timeout=60.0,
    )


def _build_gamma_prompt(outline: dict, paleta_colores: str, cantidad_slides: int) -> str:
    """
    Construye el texto de prompt para Gamma a partir del outline generado por Claude.

    Incluye el título, el resumen de cada slide, la paleta de colores (si se especificó)
    y la cantidad de slides objetivo, para guiar la generación visual de Gamma.

    Args:
        outline: Outline JSON con 'titulo_presentacion' y 'slides'.
        paleta_colores: Paleta sugerida para incluir como hint (puede ser vacía).
        cantidad_slides: Cantidad objetivo de slides para Gamma.

    Returns:
        Prompt de texto listo para enviar al endpoint de Gamma.
    """
    titulo = outline.get("titulo_presentacion", "Presentación")
    slides_texto = "\n".join(
        f"- {s.get('titulo', '')}: {s.get('contenido', '')}"
        for s in outline.get("slides", [])
    )
    paleta_hint = f"\nPaleta de colores: {paleta_colores}." if paleta_colores else ""
    return (
        f"Crea una presentación de {cantidad_slides} slides titulada '{titulo}'.\n"
        f"{slides_texto}{paleta_hint}"
    )


def publish_to_gamma(
    outline: dict,
    tema_visual: str = "minimalist",
    estilo_imagen: str = "aiGenerated",
    paleta_colores: str = "",
    cantidad_slides: int = 10,
) -> tuple[str | None, str | None]:
    """
    Publica una presentación en Gamma y solicita exportación como PPTX.

    Construye el prompt desde el outline de Claude, lo envía a la Gamma API con los
    parámetros de configuración visual y captura las URLs de resultado.

    Args:
        outline: Outline JSON con 'titulo_presentacion' y 'slides' generado por Claude.
        tema_visual: Tema visual de Gamma (style). Ej: 'minimalist', 'elegant'.
        estilo_imagen: Fuente de imágenes de Gamma (imageOptions.source).
        paleta_colores: Paleta de colores sugerida. Se incluye en el prompt.
        cantidad_slides: Cantidad objetivo de slides (numCards).

    Returns:
        Tupla (gamma_url, pptx_gamma_url):
        - gamma_url: URL pública del documento Gamma generado, o None si falla.
        - pptx_gamma_url: URL del PPTX exportado desde Gamma. None si la respuesta
          no incluye 'exportUrl' o si la llamada falla — no se lanza error.
    """
    settings = get_settings()
    prompt = _build_gamma_prompt(outline, paleta_colores, cantidad_slides)
    payload = {
        "prompt": prompt,
        "style": tema_visual,
        "imageOptions": {"source": estilo_imagen},
        "numCards": cantidad_slides,
        "exportAs": "pptx",
    }
    try:
        with httpx.Client(
            base_url="https://api.gamma.app",
            headers={"Authorization": f"Bearer {settings.gamma_api_key}"},
            timeout=60.0,
        ) as client:
            response = client.post("/ai/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            gamma_url: str | None = data.get("url") or data.get("shareUrl")
            pptx_gamma_url: str | None = data.get("exportUrl")
            return gamma_url, pptx_gamma_url
    except Exception as exc:
        log.warning(f"gamma.publish_failed | error={exc}")
        return None, None
