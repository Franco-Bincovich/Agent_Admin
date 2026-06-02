from uuid import UUID

from schemas.execution import ExecutionResponse, ExecutionStatus
from utils.errors import AppError


async def save(execution_data: dict) -> ExecutionStatus:
    """
    Crea un registro de ejecución en estado "pendiente".

    Args:
        execution_data: Datos de la ejecución a persistir.

    Returns:
        ExecutionStatus con el ID asignado.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 6.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def find_by_id(execution_id: UUID) -> ExecutionResponse | None:
    """
    Busca una ejecución por ID.

    Args:
        execution_id: UUID de la ejecución.

    Returns:
        ExecutionResponse o None.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 15.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def update_state(execution_id: UUID, fields: dict) -> ExecutionStatus:
    """
    Actualiza el estado de una ejecución (started_at, finished_at, error_message).

    Args:
        execution_id: UUID de la ejecución.
        fields: Campos a actualizar (estado, timestamps, error).

    Returns:
        ExecutionStatus actualizado.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 15.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def find_all_by_user(user_id: UUID) -> list[ExecutionStatus]:
    """
    Lista ejecuciones del usuario ordenadas por fecha descendente.

    Args:
        user_id: UUID del usuario.

    Returns:
        Lista de ExecutionStatus.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 21.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
