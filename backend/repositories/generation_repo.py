from __future__ import annotations

from integrations.supabase_client import get_supabase

_TABLE = "generaciones"


def _db():
    return get_supabase().table(_TABLE)


def create(usuario_id: str, objetivo: str, archivos: list, parametros: dict) -> dict:
    """Inserta generación con estado='procesando' y retorna el registro completo."""
    response = (
        _db()
        .insert({
            "usuario_id": str(usuario_id),
            "objetivo": objetivo,
            "archivos": archivos,
            "parametros": parametros,
            "estado": "procesando",
        })
        .execute()
    )
    return response.data[0]


def update_resultado(
    generation_id: str,
    pptx_url: str | None,
    gamma_url: str | None,
    slides_count: int,
    outline: dict,
) -> dict:
    """Actualiza a estado='listo' y persiste pptx_url, gamma_url, slides_count y outline."""
    response = (
        _db()
        .update({
            "estado": "listo",
            "pptx_url": pptx_url,
            "gamma_url": gamma_url,
            "slides_count": slides_count,
            "outline": outline,
        })
        .eq("id", str(generation_id))
        .execute()
    )
    return response.data[0]


def update_error(generation_id: str) -> None:
    """Actualiza la generación a estado='error'."""
    _db().update({"estado": "error"}).eq("id", str(generation_id)).execute()


def find_by_id(generation_id: str) -> dict | None:
    """Retorna la generación por ID, o None si no existe."""
    response = _db().select("*").eq("id", str(generation_id)).execute()
    return response.data[0] if response.data else None


def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """
    Retorna las generaciones del usuario ordenadas por creado_en DESC.
    Máximo `limit` registros (default 20).
    """
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
    """
    Retorna todas las generaciones del sistema ordenadas por creado_en DESC.
    Solo para administradores. Máximo `limit` registros (default 50).
    """
    response = (
        _db()
        .select("*")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
