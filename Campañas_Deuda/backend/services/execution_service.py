from uuid import UUID

from schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionStatus
from utils.errors import AppError

PERIODOS_VALIDOS = {"2021", "2022", "2023", "2024", "2025", "2026", "todas"}


async def create_execution(request: ExecutionCreate, user_id: UUID) -> ExecutionStatus:
    """
    Crea una ejecución en estado "pendiente" y la encola asincrónicamente.

    Valida la combinación de dimensiones. Crea el registro en DB. Dispara
    el orquestador de la cadena de agentes en background.

    Args:
        request: Parámetros de la corrida (portfolio_file_id, cartera, dureza, período).
        user_id: UUID del usuario que dispara la corrida.

    Returns:
        ExecutionStatus con estado "pendiente" e ID asignado.

    Raises:
        AppError: "INVALID_PERIODO" (422) si el período no es válido.
        AppError: "PORTFOLIO_NOT_FOUND" (404) si el archivo no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 6.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def get_execution_status(execution_id: UUID, user_id: UUID) -> ExecutionResponse:
    """
    Devuelve el estado actual de una ejecución.

    Args:
        execution_id: UUID de la ejecución.
        user_id: UUID del usuario (verificación de ownership).

    Returns:
        ExecutionResponse con estado y resultado si está listo.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe o no pertenece al usuario.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 15.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def list_executions(user_id: UUID) -> list[ExecutionStatus]:
    """
    Lista las ejecuciones del usuario ordenadas por fecha descendente.

    Args:
        user_id: UUID del usuario.

    Returns:
        Lista de ExecutionStatus.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 21.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
