from uuid import UUID

from schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionStatus
from utils.errors import AppError


async def create_execution(request: ExecutionCreate) -> ExecutionStatus:
    """
    Crea una ejecución en estado "pendiente" y la encola asincrónicamente.

    Valida que la combinación cartera/dureza/período sea válida y que el
    archivo de cartera exista y pertenezca al usuario.

    Args:
        request: Parámetros de la ejecución (portfolio_file_id, cartera, dureza, período).

    Returns:
        ExecutionStatus con estado "pendiente" e ID asignado.

    Raises:
        AppError: "PORTFOLIO_NOT_FOUND" (404) si el archivo no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 6.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def get_execution(execution_id: UUID) -> ExecutionResponse:
    """
    Devuelve el estado y resultado de una ejecución.

    Args:
        execution_id: UUID de la ejecución.

    Returns:
        ExecutionResponse con estado actual y URL del resultado si está listo.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe o no pertenece al usuario.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 15.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def list_executions() -> list[ExecutionStatus]:
    """
    Lista las ejecuciones del usuario autenticado.

    Returns:
        Lista de ExecutionStatus ordenada por fecha descendente.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 21.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
