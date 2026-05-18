from __future__ import annotations

import asyncio

from config.settings import get_settings
from integrations.gamma_client import create_generation, get_folders, poll_generation
from repositories.user_mutations_repo import update_gamma_folder_id
from utils.errors import AppError
from utils.logger import log

_POLL_INTERVAL = 3
_MAX_ATTEMPTS = 20


def _build_gamma_prompt(outline: dict, paleta_colores: str, cantidad_slides: int, titulo: str = "") -> str:
    """
    Construye el texto de prompt para Gamma a partir del outline generado por Claude.

    Incluye el título, el resumen de cada slide, la paleta de colores (si se especificó)
    y la cantidad de slides objetivo, para guiar la generación visual de Gamma.

    Args:
        outline: Outline JSON con 'titulo_presentacion' y 'slides'.
        paleta_colores: Paleta sugerida para incluir como hint (puede ser vacía).
        cantidad_slides: Cantidad objetivo de slides para Gamma.
        titulo: Título ingresado por el usuario. Tiene precedencia sobre el del outline.

    Returns:
        Prompt de texto listo para enviar al endpoint de Gamma.
    """
    titulo = titulo.strip() or outline.get("titulo_presentacion", "Presentación")
    slides_parts: list[str] = []
    for i, s in enumerate(outline.get("slides", []), start=1):
        contenido = s.get("contenido", "")
        if isinstance(contenido, list):
            contenido = "\n".join(contenido)
        slides_parts.append(f"Slide {i} — {s.get('titulo', '')}\n{contenido}")
    paleta_hint = f"\nPaleta de colores: {paleta_colores}." if paleta_colores else ""
    return (
        f"Crea una presentación de {cantidad_slides} slides titulada '{titulo}'.\n\n"
        + "\n\n".join(slides_parts)
        + paleta_hint
    )


async def resolve_user_folder(email: str, user_id: str) -> tuple[str | None, str | None]:
    """
    Busca en Gamma la carpeta cuyo nombre coincide exactamente con el email del usuario.

    Si la encuentra, persiste el folder_id en la tabla usuarios (caché) y retorna
    (folder_id, None). Si no la encuentra, retorna (None, mensaje_advertencia).
    Ante cualquier error de la API de Gamma, retorna (None, None) sin interrumpir el pipeline.

    Args:
        email: Email del usuario, usado como nombre exacto de carpeta.
        user_id: UUID del usuario en Supabase, para persistir el folder_id encontrado.

    Returns:
        Tuple (folder_id, gamma_warning). Ambos pueden ser None simultáneamente si hay error de API.
    """
    try:
        folders = await get_folders()
        for folder in folders:
            if folder.get("name", "").lower() == email.lower():
                folder_id: str = folder["id"]
                update_gamma_folder_id(user_id, folder_id)
                log.info(f"gamma.folder_found | user={email} folder_id={folder_id}")
                return folder_id, None
        log.info(f"gamma.folder_not_found | user={email}")
        return None, (
            f"Para organizar tus presentaciones en Gamma, "
            f"creá una carpeta con tu email como nombre ({email})"
        )
    except Exception as exc:
        log.warning(f"gamma.resolve_folder_error | user={email} | error={exc}")
        return None, None


async def publish_presentation(
    outline: dict,
    tema_visual: str = "minimalist",
    estilo_imagen: str = "aiGenerated",
    paleta_colores: str = "",
    cantidad_slides: int = 10,
    titulo: str = "",
    folder_id: str | None = None,
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
        titulo: Título ingresado por el usuario. Tiene precedencia sobre el del outline.

    Returns:
        Dict con 'gamma_url' y 'pptx_gamma_url'.

    Raises:
        AppError: GAMMA_FAILED 503 si la generación falla o supera el timeout de 60s.
    """
    prompt = _build_gamma_prompt(outline, paleta_colores, cantidad_slides, titulo)
    payload: dict = {
        "inputText": prompt,
        "textMode": "preserve",
        "format": "presentation",
        "numCards": cantidad_slides,
        "exportAs": "pptx",
        "imageOptions": {"source": estilo_imagen},
    }
    if folder_id:
        payload["folderIds"] = [folder_id]

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
