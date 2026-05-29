from fastapi import APIRouter, Depends, Request

from middleware.auth import get_current_user
from controllers.activity_controller import list_activity as get_activity
from utils.limiter import limiter

router = APIRouter()


@router.get("")
@limiter.limit("300/minute")
async def list_activity(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> list:
    """
    Retorna la actividad unificada del usuario autenticado
    (generaciones + documentos) ordenada por fecha DESC.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
    """
    return await get_activity(current_user["sub"])
