from __future__ import annotations

import asyncio
import json

from integrations.supabase_client import get_supabase
from utils.errors import AppError, ErrorCode
from utils.logger import log

_TABLE = "document_templates"


def _db():
    return get_supabase().table(_TABLE)


async def find_by_user(usuario_id: str) -> list[dict]:
    """
    Devuelve todas las plantillas del usuario ordenadas por creado_en desc.

    Args:
        usuario_id: UUID del usuario propietario.

    Returns:
        Lista de registros de plantillas (puede ser vacía).
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("usuario_id", str(usuario_id))
        .order("creado_en", desc=True)
        .execute()
    )
    items = response.data or []
    for item in items:
        if isinstance(item.get("secciones"), str):
            try:
                item["secciones"] = json.loads(item["secciones"])
            except Exception:
                item["secciones"] = []
    return items


async def find_by_id(template_id: str, usuario_id: str) -> dict | None:
    """
    Busca una plantilla por ID verificando ownership.

    Args:
        template_id: UUID de la plantilla.
        usuario_id: UUID del usuario; se verifica que coincida con el registro.

    Returns:
        El registro de la plantilla, o None si no existe o no pertenece al usuario.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .select("*")
        .eq("id", str(template_id))
        .eq("usuario_id", str(usuario_id))
        .execute()
    )
    data = response.data[0] if response.data else None
    if data and isinstance(data.get("secciones"), str):
        try:
            data["secciones"] = json.loads(data["secciones"])
        except Exception:
            data["secciones"] = []
    return data


async def create(
    usuario_id: str,
    nombre: str,
    secciones: list,
    is_default: bool = False,
) -> dict:
    """
    Crea una nueva plantilla de documento.

    Args:
        usuario_id: UUID del usuario propietario.
        nombre: Nombre de la plantilla (1-100 caracteres).
        secciones: Lista de identificadores de sección a guardar.
        is_default: Si True, esta plantilla se marca como predeterminada.

    Returns:
        El registro completo de la plantilla recién creada.

    Raises:
        AppError: INTERNAL_ERROR 500 si la inserción falla.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .insert({
            "usuario_id": str(usuario_id),
            "nombre": nombre,
            "secciones": json.dumps([s.model_dump() if hasattr(s, "model_dump") else s for s in secciones]),
            "is_default": is_default,
        })
        .execute()
    )
    return response.data[0]


async def update(
    template_id: str,
    usuario_id: str,
    nombre: str,
    secciones: list,
    is_default: bool,
) -> dict | None:
    """
    Actualiza una plantilla verificando ownership.

    Args:
        template_id: UUID de la plantilla a actualizar.
        usuario_id: UUID del usuario; se usa como filtro de ownership.
        nombre: Nuevo nombre de la plantilla.
        secciones: Nueva lista de identificadores de sección.
        is_default: Nuevo valor del flag de plantilla predeterminada.

    Returns:
        El registro actualizado, o None si no existe o no pertenece al usuario.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .update({
            "nombre": nombre,
            "secciones": json.dumps([s.model_dump() if hasattr(s, "model_dump") else s for s in secciones]),
            "is_default": is_default,
        })
        .eq("id", str(template_id))
        .eq("usuario_id", str(usuario_id))
        .execute()
    )
    return response.data[0] if response.data else None


async def delete(template_id: str, usuario_id: str) -> bool:
    """
    Elimina una plantilla verificando ownership.

    Args:
        template_id: UUID de la plantilla a eliminar.
        usuario_id: UUID del usuario; se usa como filtro de ownership.

    Returns:
        True si se eliminó al menos un registro, False si no existía o no era del usuario.
    """
    response = await asyncio.to_thread(
        lambda: _db()
        .delete()
        .eq("id", str(template_id))
        .eq("usuario_id", str(usuario_id))
        .execute()
    )
    return bool(response.data)


async def set_default(template_id: str, usuario_id: str) -> dict | None:
    """
    Marca una plantilla como default y desmarca las demás del mismo usuario.

    Opera en dos pasos: primero desmarca todas las plantillas del usuario,
    luego marca la plantilla indicada. Si la plantilla no existe o no pertenece
    al usuario, retorna None sin modificar el estado.

    Args:
        template_id: UUID de la plantilla que pasará a ser default.
        usuario_id: UUID del usuario propietario.

    Returns:
        El registro de la plantilla actualizada, o None si no existe o no es del usuario.
    """
    await asyncio.to_thread(
        lambda: _db()
        .update({"is_default": False})
        .eq("usuario_id", str(usuario_id))
        .execute()
    )
    response = await asyncio.to_thread(
        lambda: _db()
        .update({"is_default": True})
        .eq("id", str(template_id))
        .eq("usuario_id", str(usuario_id))
        .execute()
    )
    log.info(
        "document_template.set_default",
        extra={"template_id": template_id, "usuario_id": usuario_id},
    )
    return response.data[0] if response.data else None
