from repositories import user_mutations_repo, user_repo
from schemas.user import UserResponse
from utils.errors import AppError, ErrorCode


async def update_user_active(user_id: str, activo: bool, requester_id: str) -> UserResponse:
    """
    Activa o desactiva un usuario. Solo debe invocarse para administradores.
    Un administrador no puede desactivarse a sí mismo.

    Args:
        user_id: UUID del usuario a modificar.
        activo: True para activar, False para desactivar.
        requester_id: UUID del administrador que realiza la acción.

    Returns:
        UserResponse con los datos actualizados del usuario.

    Raises:
        AppError: code FORBIDDEN (403) si el administrador intenta desactivarse a sí mismo.
        AppError: code NOT_FOUND (404) si el usuario no existe.
    """
    if not activo and user_id == requester_id:
        raise AppError(
            "Un administrador no puede desactivarse a sí mismo.",
            ErrorCode.FORBIDDEN,
            403,
        )
    updated = await user_mutations_repo.update_active(user_id, activo)
    return UserResponse(**updated)


async def update_user_role(user_id: str, rol: str, requester_id: str) -> UserResponse:
    """
    Cambia el rol de un usuario. Solo debe invocarse para administradores.
    Un admin no puede cambiarse el rol a sí mismo (evita auto-degradarse y perder
    el acceso admin); sí puede cambiar el rol de otros administradores. El rol llega
    ya validado contra los 3 valores por el schema.

    Raises:
        AppError FORBIDDEN 403 si el admin intenta cambiarse su propio rol.
        AppError NOT_FOUND 404 si el usuario no existe.
    """
    if user_id == requester_id:
        raise AppError(
            "Un administrador no puede cambiar su propio rol.",
            ErrorCode.FORBIDDEN,
            403,
        )
    updated = await user_mutations_repo.update_rol(user_id, rol)
    return UserResponse(**updated)


async def update_user_manager(user_id: str, manager_id: str | None, requester_id: str) -> UserResponse:
    """
    Asigna, cambia o desasigna el manager (gerente) de un usuario líder.
    Solo debe invocarse para administradores.

    El cambio de manager tiene EFECTO INMEDIATO: la jerarquía se resuelve leyendo la
    DB en cada request de escritura, NO viaja en el token (a diferencia del rol, que
    solo se actualiza al refrescar/re-loguear). No se emiten ni invalidan tokens acá.

    Reglas:
    - El target debe existir y tener rol 'lider' (solo los líderes cuelgan de un gerente).
    - Si manager_id no es None, el manager debe existir y tener rol 'gerente'.
    - Un usuario no puede ser su propio manager.
    - manager_id None desasigna (NULL) sin validar rol de manager.

    Args:
        user_id: UUID del usuario líder a modificar.
        manager_id: UUID del gerente, o None para desasignar.
        requester_id: UUID del administrador que realiza la acción.

    Returns:
        UserResponse con los datos actualizados del usuario.

    Raises:
        AppError VALIDATION_ERROR 400 si user_id == manager_id (auto-referencia).
        AppError NOT_FOUND 404 si el target o el manager no existen.
        AppError VALIDATION_ERROR 409 si el target no es 'lider' o el manager no es 'gerente'.
    """
    if manager_id is not None and manager_id == user_id:
        raise AppError(
            "Un usuario no puede ser su propio manager.",
            ErrorCode.VALIDATION_ERROR,
            400,
        )
    target = await user_repo.find_by_id(user_id)
    if not target:
        raise AppError("Usuario no encontrado", ErrorCode.NOT_FOUND, 404)
    if target["rol"] != "lider":
        raise AppError(
            "Solo se puede asignar manager a un usuario con rol lider.",
            ErrorCode.VALIDATION_ERROR,
            409,
        )
    if manager_id is not None:
        manager = await user_repo.find_by_id(manager_id)
        if not manager:
            raise AppError("Manager no encontrado", ErrorCode.NOT_FOUND, 404)
        if manager["rol"] != "gerente":
            raise AppError(
                "El manager debe tener rol gerente.",
                ErrorCode.VALIDATION_ERROR,
                409,
            )
    updated = await user_mutations_repo.update_manager(user_id, manager_id)
    return UserResponse(**updated)


async def delete_user(user_id: str, requester_id: str) -> None:
    """
    Elimina un usuario permanentemente (hard delete).
    No permite que un admin se elimine a sí mismo.

    Args:
        user_id: ID del usuario a eliminar.
        requester_id: ID del admin que ejecuta la acción.

    Raises:
        AppError FORBIDDEN 403 si intenta eliminarse a sí mismo.
        AppError NOT_FOUND 404 si el usuario no existe.
    """
    if user_id == requester_id:
        raise AppError("No podés eliminar tu propia cuenta", ErrorCode.FORBIDDEN, 403)
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise AppError("Usuario no encontrado", ErrorCode.NOT_FOUND, 404)
    await user_mutations_repo.delete(user_id)
