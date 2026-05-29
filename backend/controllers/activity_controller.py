from services.activity_service import get_user_activity


async def list_activity(user_id: str) -> list:
    """
    Devuelve la actividad reciente del usuario.

    Args:
        user_id: ID del usuario autenticado.

    Returns:
        Lista de items de actividad ordenados por fecha descendente.
    """
    return await get_user_activity(user_id)
