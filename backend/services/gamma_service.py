from __future__ import annotations

import asyncio

from config.settings import get_settings
from integrations.gamma_client import create_generation, poll_generation
from utils.errors import AppError
from utils.logger import log

_POLL_INTERVAL = 3
_MAX_ATTEMPTS = 20


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


async def publish_presentation(
    outline: dict,
    tema_visual: str = "minimalist",
    estilo_imagen: str = "aiGenerated",
    paleta_colores: str = "",
    cantidad_slides: int = 10,
) -> dict[str, str]:
    """
    Publica una presentación en Gamma API v1.0 y espera a que complete.

    Construye el prompt desde el outline de Claude, crea la generación vía POST /generations,
    y realiza polling hasta obtener status 'completed' o 'failed' (máximo 20 intentos, 60s).

    Args:
        outline: Outline JSON con 'titulo_presentacion' y 'slides' generado por Claude.
        tema_visual: Identificador de tema visual. Se mapea a 'themeId' solo si
            settings expone gamma_theme_ids; de lo contrario se omite.
        estilo_imagen: Fuente de imágenes para Gamma (imageOptions.source).
            Ej: 'aiGenerated', 'pexels'.
        paleta_colores: Paleta de colores sugerida. Se incluye en el prompt como hint.
        cantidad_slides: Cantidad objetivo de slides. Rango recomendado: 5-20.

    Returns:
        Dict con 'gamma_url' y 'pptx_gamma_url'.

    Raises:
        AppError: GAMMA_FAILED 503 si la generación falla o supera el timeout de 60s.
    """
    prompt = _build_gamma_prompt(outline, paleta_colores, cantidad_slides)
    payload: dict = {
        "inputText": prompt,
        "textMode": "preserve",
        "format": "presentation",
        "numCards": cantidad_slides,
        "exportAs": "pptx",
        "imageOptions": {"source": estilo_imagen},
    }

    settings = get_settings()
    if tema_visual and hasattr(settings, "gamma_theme_ids"):
        theme_map = settings.gamma_theme_ids  # type: ignore[attr-defined]
        if isinstance(theme_map, dict) and tema_visual in theme_map:
            payload["themeId"] = theme_map[tema_visual]

    log.info(f"gamma.create_generation | numCards={cantidad_slides}")
    data = await create_generation(payload)
    generation_id: str = data["generationId"]

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        await asyncio.sleep(_POLL_INTERVAL)
        result = await poll_generation(generation_id)
        status: str = result.get("status", "")
        log.info(f"gamma.poll | attempt={attempt} generationId={generation_id} status={status}")

        if status == "completed":
            return {
                "gamma_url": result.get("gammaUrl", ""),
                "pptx_gamma_url": result.get("exportUrl", ""),
            }
        if status == "failed":
            raise AppError("Gamma generation failed", "GAMMA_FAILED", 503)

    raise AppError("Gamma generation timed out", "GAMMA_FAILED", 503)
