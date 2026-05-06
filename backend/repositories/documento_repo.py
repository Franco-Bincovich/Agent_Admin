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
    """
    Inserta un nuevo documento con estado='procesando' y retorna el registro completo.

    Args:
        usuario_id: UUID del usuario propietario del documento.
        titulo: Título del documento a generar.
        archivos: Lista de nombres de archivos fuente subidos.
        plantilla_nombre: Nombre del archivo de plantilla (opcional).
        secciones: Secciones requeridas en el documento final.
        indicaciones: Indicaciones adicionales del usuario (opcional).
        opciones: Dict con las opciones de procesamiento (homogeneizar, deduplicar, usar_imagenes).

    Returns:
        Registro completo del documento insertado, incluyendo su ID asignado.
    """
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
    """
    Actualiza el documento a estado='listo' y persiste la URL del DOCX generado.

    Args:
        documento_id: UUID del documento a actualizar.
        docx_url: URL pública del archivo .docx en Supabase Storage.

    Returns:
        Registro actualizado del documento.
    """
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


def find_by_id(documento_id: str) -> dict | None:
    """Retorna el documento por ID, o None si no existe."""
    response = _db().select("*").eq("id", str(documento_id)).execute()
    return response.data[0] if response.data else None


def find_by_user(usuario_id: str, limit: int = 20) -> list[dict]:
    """
    Retorna los documentos del usuario ordenados por creado_en DESC.

    Args:
        usuario_id: UUID del usuario propietario.
        limit: Número máximo de registros a retornar (default 20).

    Returns:
        Lista de documentos ordenada por fecha de creación descendente.
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
    Retorna todos los documentos del sistema ordenados por creado_en DESC.

    Solo para administradores. Máximo `limit` registros (default 50).

    Args:
        limit: Número máximo de registros a retornar.

    Returns:
        Lista de todos los documentos ordenada por fecha de creación descendente.
    """
    response = (
        _db()
        .select("*")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
