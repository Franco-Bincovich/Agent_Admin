from __future__ import annotations

from integrations.supabase_client import get_supabase
from utils.errors import AppError, ErrorCode

_TABLE = "usuarios"


def create(email: str, nombre: str, password_hash: str, rol: str) -> dict:
    """Inserta un usuario nuevo. Nunca almacenar password en texto plano."""
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


def create_full(email: str, nombre: str, username: str, password_hash: str, rol: str) -> dict:
    """Inserta un usuario con username. Usar en lugar de create() cuando se provee username."""
    data = {
        "email": email,
        "nombre": nombre,
        "username": username,
        "password_hash": password_hash,
        "rol": rol,
        "activo": True,
    }
    response = get_supabase().table(_TABLE).insert(data).execute()
    if not response.data:
        raise AppError("No se pudo crear el usuario.", ErrorCode.INTERNAL_ERROR, 500)
    return response.data[0]


def update_profile(user_id: str, fields: dict) -> dict:
    """Actualiza campos arbitrarios de un usuario por su ID. Nunca incluir password en texto plano."""
    response = (
        get_supabase()
        .table(_TABLE)
        .update(fields)
        .eq("id", user_id)
        .execute()
    )
    if not response.data:
        raise AppError("Usuario no encontrado.", ErrorCode.NOT_FOUND, 404)
    return response.data[0]


def update_active(user_id: str, activo: bool) -> dict:
    """Activa o desactiva un usuario por su ID."""
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
