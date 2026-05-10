from __future__ import annotations

from datetime import datetime

from integrations.supabase_client import get_supabase
from utils.errors import AppError, ErrorCode

_TABLE = "refresh_tokens"


def save(user_id: str, token_hash: str, expires_at: datetime) -> dict:
    """
    Persiste un refresh token hasheado en DB.

    Args:
        user_id: UUID del propietario del token.
        token_hash: Hash bcrypt del token en texto plano — nunca el token crudo.
        expires_at: Fecha y hora de expiración del token.

    Returns:
        Fila insertada con id, user_id, token_hash, created_at y expires_at.

    Raises:
        AppError: INTERNAL_ERROR 500 si la inserción falla.
    """
    data = {
        "user_id": user_id,
        "token_hash": token_hash,
        "expires_at": expires_at.isoformat(),
    }
    response = get_supabase().table(_TABLE).insert(data).execute()
    if not response.data:
        raise AppError("No se pudo guardar el refresh token.", ErrorCode.INTERNAL_ERROR, 500)
    return response.data[0]


def find_by_user(user_id: str) -> dict | None:
    """
    Retorna el refresh token más reciente de un usuario.

    Args:
        user_id: UUID del usuario como string.

    Returns:
        Fila del token o None si el usuario no tiene refresh token activo.
    """
    response = (
        get_supabase()
        .table(_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def delete(token_id: str) -> None:
    """
    Elimina un refresh token por su ID. Usar en rotación.

    Args:
        token_id: UUID del registro de refresh_token a eliminar.
    """
    get_supabase().table(_TABLE).delete().eq("id", token_id).execute()


def delete_all_by_user(user_id: str) -> None:
    """
    Elimina todos los refresh tokens de un usuario. Usar en logout.

    No alcanza con que el cliente descarte el token — debe borrarse de DB
    para que no pueda reutilizarse (SEGURIDAD-PENTEST 2.5).

    Args:
        user_id: UUID del usuario como string.
    """
    get_supabase().table(_TABLE).delete().eq("user_id", user_id).execute()
