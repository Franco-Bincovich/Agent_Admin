from __future__ import annotations

from repositories import planificacion_area_repo, user_repo
from utils.errors import AppError, ErrorCode


async def assert_puede_mutar_tarea(tarea: dict, current_user: dict) -> None:
    """Punto único de autorización de escritura sobre una tarea (Modelo A).

    Decide si current_user puede mutar el avance de la tarea ya fetcheada
    (marcar completada, actualizar progreso, reprogramar). Lanza AppError
    FORBIDDEN 403 si no puede; retorna None si puede.

    Regla:
      - administrador: cualquier tarea.
      - tarea sin área (area_id None) o área sin dueño (gerente_id None):
        abierto a cualquier usuario autenticado (estado transitorio).
      - área con dueño: solo el gerente dueño y los líderes cuyo manager_id
        apunta a ese gerente. Nadie más.

    Toda la política del modelo de permisos vive acá: migrar al Modelo B en el
    futuro es editar esta única función.

    Args:
        tarea: Fila de la tarea ya leída (debe incluir area_id).
        current_user: Payload JWT del usuario autenticado (role + sub).

    Raises:
        AppError: code 'FORBIDDEN', status 403 si el usuario no puede mutar.
    """
    role = current_user.get("role")
    if role == "administrador":
        return

    area_id = tarea.get("area_id")
    if area_id is None:
        return

    area = await planificacion_area_repo.find_by_id(area_id)
    gerente_id = area.get("gerente_id") if area else None
    if gerente_id is None:
        return

    sub = current_user.get("sub")
    if role == "gerente" and sub == gerente_id:
        return
    if role == "lider":
        usuario = await user_repo.find_by_id(sub)
        if usuario and usuario.get("manager_id") == gerente_id:
            return

    raise AppError("No autorizado", ErrorCode.FORBIDDEN, 403)
