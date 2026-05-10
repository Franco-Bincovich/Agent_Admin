from __future__ import annotations

from integrations.supabase_client import get_supabase

_TABLE = "documentos"


def _db():
    return get_supabase().table(_TABLE)


def create(
    usuario_id: str,
    titulo: str,
    archivos: list,
    plantilla_nombre: str | None,
    secciones: list,
    indicaciones: str | None,
    opciones: dict,
) -> dict:
    """Inserta un documento con estado='procesando' y retorna el registro completo."""
    response = (
        _db()
        .insert({
            "usuario_id": str(usuario_id),
            "titulo": titulo,
            "archivos": archivos,
            "plantilla_nombre": plantilla_nombre,
            "secciones": secciones,
            "indicaciones": indicaciones,
            "opciones": opciones,
            "estado": "procesando",
        })
        .execute()
    )
    return response.data[0]


def update_resultado(documento_id: str, docx_url: str) -> dict:
    """Actualiza el documento a estado='listo' y persiste la URL del DOCX generado."""
    response = (
        _db()
        .update({"estado": "listo", "docx_url": docx_url})
        .eq("id", str(documento_id))
        .execute()
    )
    return response.data[0]


def update_error(documento_id: str) -> None:
    """Actualiza el documento a estado='error'."""
    _db().update({"estado": "error"}).eq("id", str(documento_id)).execute()
