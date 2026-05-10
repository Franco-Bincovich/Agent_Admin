from __future__ import annotations

from integrations.supabase_client import get_supabase

_TABLE = "documentos"


def _db():
    return get_supabase().table(_TABLE)


def find_by_id(documento_id: str) -> dict | None:
    """Retorna el documento por ID, o None si no existe."""
    response = _db().select("*").eq("id", str(documento_id)).execute()
    return response.data[0] if response.data else None


def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """Retorna los documentos del usuario ordenados por creado_en DESC."""
    response = (
        _db()
        .select("*")
        .eq("usuario_id", str(usuario_id))
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


def find_all(limit: int = 50) -> list[dict]:
    """Retorna todos los documentos del sistema ordenados por creado_en DESC. Solo para administradores."""
    response = (
        _db()
        .select("*")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
