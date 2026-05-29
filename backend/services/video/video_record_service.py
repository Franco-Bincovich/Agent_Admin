from __future__ import annotations

from repositories import video_repo
from utils.errors import AppError, ErrorCode


async def create_video_job(
    usuario_id: str,
    titulo: str,
    video_input_url: str,
    parametros: dict,
) -> dict:
    """
    Inserta un video job con estado='pending' en la DB y retorna el registro.

    Args:
        usuario_id: UUID del usuario que inicia el job.
        titulo: Título descriptivo del job.
        video_input_url: URL pública del video fuente en Supabase Storage.
        parametros: Dict con las variantes de edición y configuración adicional.

    Returns:
        Dict con los datos del registro creado, incluyendo el ID asignado.
    """
    return await video_repo.create(usuario_id, titulo, video_input_url, parametros)


async def get_video_job(job_id: str, usuario_id: str) -> dict:
    """
    Retorna un video job verificando ownership. Devuelve 404 si no existe
    o si el job no pertenece al usuario — nunca 403 (SEGURIDAD 2.4).

    Args:
        job_id: UUID del job a buscar.
        usuario_id: UUID del usuario autenticado (del JWT).

    Returns:
        Dict con los datos del job.

    Raises:
        AppError: code NOT_FOUND (404) si no existe o el usuario no tiene acceso.
    """
    job = await video_repo.find_by_id(job_id)
    if not job or job["usuario_id"] != usuario_id:
        raise AppError("Video job no encontrado.", ErrorCode.NOT_FOUND, 404)
    return job


async def list_video_jobs(usuario_id: str) -> list[dict]:
    """
    Retorna los video jobs del usuario ordenados por creado_en DESC.

    Args:
        usuario_id: UUID del usuario propietario.

    Returns:
        Lista de dicts con los jobs del usuario.
    """
    return await video_repo.find_by_user(usuario_id)
