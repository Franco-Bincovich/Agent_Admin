from uuid import UUID

from fastapi import APIRouter

from controllers import execution_controller
from schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionStatus

router = APIRouter()


@router.post("/", response_model=ExecutionStatus, status_code=202)
async def create_execution(body: ExecutionCreate) -> ExecutionStatus:
    """
    Dispara una corrida de análisis (async). Devuelve 202 con el estado inicial.
    Stub — implementar en Sesión 6 (formulario) y Sesión 15 (async).
    """
    return await execution_controller.create_execution(body)


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: UUID) -> ExecutionResponse:
    """Estado y resultado de una ejecución. Stub — implementar en Sesión 15."""
    return await execution_controller.get_execution(execution_id)


@router.get("/", response_model=list[ExecutionStatus])
async def list_executions() -> list[ExecutionStatus]:
    """Historial de ejecuciones del usuario. Stub — implementar en Sesión 21."""
    return await execution_controller.list_executions()
