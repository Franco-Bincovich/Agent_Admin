from __future__ import annotations

from integrations.supabase_client import get_supabase
from utils.errors import AppError, ErrorCode

_TABLE = "usuarios"


def find_by_email(email: str) -> dict | None:
    """
    Busca un usuario por email.

    Args:
        email: Dirección de email a buscar.

    Returns:
        Dict con los datos del usuario o None si no existe.
    """
    response = get_supabase().table(_TABLE).select("*").eq("email", email).execute()
    return response.data[0] if response.data else None


def find_by_id(user_id: str) -> dict | None:
    """
    Busca un usuario por su ID (UUID).

    Args:
        user_id: UUID del usuario como string.

    Returns:
        Dict con los datos del usuario o None si no existe.
    """
    response = get_supabase().table(_TABLE).select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def create(email: str, nombre: str, password_hash: str, rol: str) -> dict:
    """
    Inserta un usuario nuevo en la tabla users.

    Args:
        email: Email único del usuario.
        nombre: Nombre completo.
        password_hash: Hash bcrypt de la contraseña — nunca texto plano.
        rol: Rol del usuario. Valores: 'administrador' | 'editor' | 'viewer'.

    Returns:
        Dict con los datos del usuario creado (incluye id y created_at generados por DB).

    Raises:
        AppError: code 'INTERNAL_ERROR', status 500 si la inserción falla.
    """
    data = {
        "email": email,
        "nombre": nombre,
        "password_hash": password_hash,
        "rol": rol,
        "activo": True,
    }
    response = get_supabase().table(_TABLE).insert(data).execute()
    if not response.data:
        raise AppError("No se pudo crear el usuario.", ErrorCode.INTERNAL_ERROR, 500)
    return response.data[0]


def find_all() -> list[dict]:
    """Retorna todos los usuarios del sistema ordenados por creado_en DESC."""
    response = get_supabase().table(_TABLE).select("*").order("creado_en", desc=True).execute()
    return response.data


def update_active(user_id: str, activo: bool) -> dict:
    """
    Activa o desactiva un usuario por su ID.

    Args:
        user_id: UUID del usuario como string.
        activo: True para activar, False para desactivar.

    Returns:
        Dict con los datos actualizados del usuario.

    Raises:
        AppError: code 'NOT_FOUND', status 404 si el usuario no existe.
    """
    response = (
        get_supabase()
        .table(_TABLE)
        .update({"activo": activo})
        .eq("id", user_id)
        .execute()
    )
    if not response.data:
        raise AppError("Usuario no encontrado.", ErrorCode.NOT_FOUND, 404)
    return response.data[0]
