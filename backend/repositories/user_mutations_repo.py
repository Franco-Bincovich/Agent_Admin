from __future__ import annotations

import asyncio

from integrations.supabase_client import get_supabase
from utils.errors import AppError, ErrorCode

_TABLE = "usuarios"


async def create(email: str, nombre: str, password_hash: str, rol: str) -> dict:
    """Inserta un usuario nuevo. Nunca almacenar password en texto plano."""
    data = {
        "email": email,
        "nombre": nombre,
        "password_hash": password_hash,
        "rol": rol,
        "activo": True,
    }
    response = await asyncio.to_thread(
        lambda: get_supabase().table(_TABLE).insert(data).execute()
    )
    if not response.data:
        raise AppError("No se pudo crear el usuario.", ErrorCode.INTERNAL_ERROR, 500)
    return response.data[0]


async def create_full(email: str, nombre: str, username: str, password_hash: str, rol: str) -> dict:
    """Inserta un usuario con username. Usar en lugar de create() cuando se provee username."""
    data = {
        "email": email,
        "nombre": nombre,
        "username": username,
        "password_hash": password_hash,
        "rol": rol,
        "activo": True,
    }
    response = await asyncio.to_thread(
        lambda: get_supabase().table(_TABLE).insert(data).execute()
    )
    if not response.data:
        raise AppError("No se pudo crear el usuario.", ErrorCode.INTERNAL_ERROR, 500)
    return response.data[0]


async def update_profile(user_id: str, fields: dict) -> dict:
    """Actualiza campos arbitrarios de un usuario por su ID. Nunca incluir password en texto plano."""
    response = await asyncio.to_thread(
        lambda: get_supabase()
        .table(_TABLE)
        .update(fields)
        .eq("id", user_id)
        .execute()
    )
    if not response.data:
        raise AppError("Usuario no encontrado.", ErrorCode.NOT_FOUND, 404)
    return response.data[0]


async def update_active(user_id: str, activo: bool) -> dict:
    """Activa o desactiva un usuario por su ID."""
    response = await asyncio.to_thread(
        lambda: get_supabase()
        .table(_TABLE)
        .update({"activo": activo})
        .eq("id", user_id)
        .execute()
    )
    if not response.data:
        raise AppError("Usuario no encontrado.", ErrorCode.NOT_FOUND, 404)
    return response.data[0]


async def update_gamma_folder_id(user_id: str, folder_id: str) -> None:
    """Persiste el ID de carpeta Gamma del usuario para evitar lookups repetidos."""
    await asyncio.to_thread(
        lambda: get_supabase().table(_TABLE).update({"gamma_folder_id": folder_id}).eq("id", user_id).execute()
    )
