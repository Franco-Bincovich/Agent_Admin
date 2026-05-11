from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from middleware.auth import get_current_user
from services.activity_service import get_user_activity

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("")
@limiter.limit("60/minute")
def list_activity(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> list:
    """
    Retorna la actividad unificada del usuario autenticado
    (generaciones + documentos) ordenada por fecha DESC.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
    """
    return get_user_activity(current_user["sub"])
