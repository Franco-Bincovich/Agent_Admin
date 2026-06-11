"""
Wrapper de la API de Anthropic (Claude).

El system prompt SIEMPRE se pasa separado del input del usuario para
prevenir prompt injection (SEGURIDAD-PENTEST §6.1).
Sin conexión real hasta Sesión 10.
"""

from config.settings import settings
from utils.errors import AppError
from utils.logger import logger

MAX_TOKENS = 4096


async def generate(system_prompt: str, user_input: str, model: str = "claude-sonnet-4-6") -> str:
    """
    Llama a la API de Anthropic y devuelve el texto generado.

    El system_prompt se pasa en el campo 'system' (siempre separado del
    input del usuario para prevenir prompt injection).

    Args:
        system_prompt: Instrucciones del sistema (rol + reglas del agente).
        user_input: Input del usuario ya sanitizado.
        model: Modelo a usar. Default: claude-sonnet-4-6.

    Returns:
        Texto generado por el modelo.

    Raises:
        AppError: "CLAUDE_UNAVAILABLE" (503) si la API no responde.
        AppError: "GENERATION_FAILED" (500) si el modelo no produce output válido.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 10.
    """
    if not settings.anthropic_api_key:
        raise AppError("Anthropic API key no configurada", "CLAUDE_UNAVAILABLE", 503)
    logger.info("Llamada a Anthropic (stub)", extra={"model": model})
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def health_check() -> bool:
    """
    Verifica que la API de Anthropic esté disponible antes de una corrida.

    Returns:
        True si la API responde correctamente.

    Raises:
        AppError: "CLAUDE_UNAVAILABLE" (503) si no responde.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 10.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
