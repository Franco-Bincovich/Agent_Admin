"""
Wrapper de la API de Perplexity.

Usado exclusivamente por el Agente 3 (Economista) para obtener contexto
macroeconómico en tiempo real. BCRA e INDEC están excluidos por disponibilidad.
Sin conexión real hasta Sesión 9.
"""

from config.settings import settings
from utils.errors import AppError
from utils.logger import logger


async def get_economic_context(query: str) -> str:
    """
    Consulta Perplexity para obtener contexto económico actual relevante.

    La consulta se focaliza en indicadores de la economía del conurbano
    bonaerense: inflación, empleo, salarios, capacidad de pago.

    Args:
        query: Consulta de contexto económico para el Agente 3.

    Returns:
        Texto con el contexto económico relevante obtenido de Perplexity.

    Raises:
        AppError: "PERPLEXITY_UNAVAILABLE" (503) si la API no responde.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 9.
    """
    if not settings.perplexity_api_key:
        raise AppError("Perplexity API key no configurada", "PERPLEXITY_UNAVAILABLE", 503)
    logger.info("Consulta a Perplexity (stub)", extra={"query_length": len(query)})
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def health_check() -> bool:
    """
    Verifica disponibilidad de la API de Perplexity antes de una corrida.

    Ante falla, el Agente 3 continúa sin contexto externo (degradación elegante)
    y lo documenta en el informe — nunca abortar la entrega.

    Returns:
        True si la API responde correctamente.

    Raises:
        AppError: "PERPLEXITY_UNAVAILABLE" (503) si no responde.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 9.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
