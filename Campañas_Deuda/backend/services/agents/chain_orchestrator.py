from utils.errors import AppError
from utils.logger import logger


async def run_chain(portfolio_data: dict, execution_id: str) -> dict:
    """
    Orquestador de la cadena de 4 agentes + loop de revisión.

    Corre los agentes en orden:
        1. debt_management_agent.analyze_portfolio()
        2. revenue_director_agent.critique_strategy()
        3. economist_agent.analyze_with_context()  ← incluye Perplexity
        4. executive_agent.synthesize_final_strategy()

    Después de la pasada inicial, corre una sola iteración de revisión
    en la que cada agente revisa las tres estrategias antes de que el
    Ejecutivo haga la síntesis final. No hay loops abiertos (control de
    costos y estabilidad).

    Si un servicio externo falla (Anthropic/Perplexity), aplica degradación
    elegante: continúa la cadena sin el contexto fallido y lo documenta
    en el informe (nunca abortar la entrega).

    Args:
        portfolio_data: Datos agregados de la cartera (output del parser).
        execution_id: UUID de la ejecución (para logging y trazabilidad).

    Returns:
        Diccionario con:
            - agent1: dict (output de Gestión de Deuda)
            - agent2: dict (output de Director de Rentas)
            - agent3: dict (output de Economista)
            - final: dict (síntesis ejecutiva)
            - degradaciones: list[str] (servicios que fallaron y cómo se manejó)

    Raises:
        AppError: "CHAIN_FAILED" (500) si la cadena no puede completarse mínimamente.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 14.
    """
    logger.info("Iniciando cadena de agentes", extra={"execution_id": execution_id})
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
