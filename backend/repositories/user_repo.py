from __future__ import annotations

from integrations.supabase_client import get_supabase

_TABLE = "usuarios"


def find_by_email(email: str) -> dict | None:
    response = get_supabase().table(_TABLE).select("*").eq("email", email).execute()
    return response.data[0] if response.data else None


def find_by_username(username: str) -> dict | None:
    response = get_supabase().table(_TABLE).select("*").eq("username", username).execute()
    return response.data[0] if response.data else None


def find_by_id(user_id: str) -> dict | None:
    response = get_supabase().table(_TABLE).select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def find_all() -> list[dict]:
    """Retorna todos los usuarios del sistema ordenados por creado_en DESC."""
    response = get_supabase().table(_TABLE).select("*").order("creado_en", desc=True).execute()
    return response.data
