from __future__ import annotations

from integrations.supabase_client import get_supabase

_TABLE = "video_brand_config"


def _db():
    return get_supabase().table(_TABLE)


def get_by_user(usuario_id: str) -> dict | None:
    """
    Retorna la configuración de marca del usuario, o None si todavía no la configuró.

    Args:
        usuario_id: UUID del usuario propietario de la config.

    Returns:
        Dict con el registro de brand config, o None si no existe.
    """
    response = _db().select("*").eq("usuario_id", str(usuario_id)).execute()
    return response.data[0] if response.data else None


def upsert(
    usuario_id: str,
    logo_url: str | None = None,
    color_primario: str | None = None,
    color_secundario: str | None = None,
    fuente: str | None = None,
) -> dict:
    """
    Crea o actualiza la configuración de marca del usuario.

    La restricción UNIQUE en usuario_id garantiza una sola fila por usuario.
    Si ya existe, el upsert sobreescribe todos los campos provistos — incluso
    con None, lo que permite borrar valores previamente guardados.

    Args:
        usuario_id: UUID del usuario propietario.
        logo_url: URL del logo en Storage. None deja el campo en NULL.
        color_primario: Color primario en formato hexadecimal (ej. '#1E40AF'). None → NULL.
        color_secundario: Color secundario en formato hexadecimal. None → NULL.
        fuente: Nombre de la fuente tipográfica. None → NULL.

    Returns:
        Dict con el registro completo después del upsert.
    """
    response = (
        _db()
        .upsert(
            {
                "usuario_id": str(usuario_id),
                "logo_url": logo_url,
                "color_primario": color_primario,
                "color_secundario": color_secundario,
                "fuente": fuente,
                "actualizado_en": "now()",
            },
            on_conflict="usuario_id",
        )
        .execute()
    )
    return response.data[0]
