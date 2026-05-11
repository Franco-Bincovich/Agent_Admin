from __future__ import annotations

from repositories import documento_repo, generation_repo
from utils.logger import log


def get_user_activity(user_id: str) -> list[dict]:
    """
    Retorna la actividad unificada del usuario: generaciones + documentos,
    ordenados por creado_en DESC.

    Args:
        user_id: UUID del usuario autenticado.

    Returns:
        Lista de dicts con campo adicional 'tipo': 'presentacion' | 'documento'.
    """
    log.info("get_user_activity", extra={"user_id": str(user_id)})
    generaciones = generation_repo.find_by_user(user_id)
    documentos = documento_repo.find_by_user(user_id)

    items = (
        [{**g, "tipo": "presentacion"} for g in generaciones]
        + [{**d, "tipo": "documento"} for d in documentos]
    )
    items.sort(key=lambda x: x.get("creado_en", ""), reverse=True)
    return items
