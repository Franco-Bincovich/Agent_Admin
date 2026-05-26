from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, UploadFile

from integrations.supabase_client import get_supabase
from schemas.video import VarianteConfig, VideoJobResponse
from services.video.video_job_service import run_video_job
from services.video.video_record_service import (
    create_video_job,
    get_video_job,
    list_video_jobs,
)
from utils.errors import AppError, ErrorCode

_BUCKET = "videos-input"


def _upload_video(video_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Sube los bytes del video al bucket de Supabase Storage y retorna la URL pública.

    El path en Storage es un UUID para evitar colisiones, preservando
    la extensión original para que el worker de Fase 2 identifique el formato.

    Args:
        video_bytes: Contenido binario del archivo de video.
        filename: Nombre original del archivo (se usa solo para extraer la extensión).
        content_type: MIME type del video (ej. 'video/mp4').

    Returns:
        URL pública del archivo en Supabase Storage.
    """
    ext = Path(filename).suffix or ".mp4"
    path = f"{uuid4()}{ext}"
    storage = get_supabase().storage.from_(_BUCKET)
    storage.upload(path=path, file=video_bytes, file_options={"content-type": content_type})
    return storage.get_public_url(path)


async def create_job(
    video: UploadFile,
    titulo: str,
    variantes_raw: str,
    background_tasks: BackgroundTasks,
    current_user: dict,
) -> VideoJobResponse:
    """
    Orquesta la creación de un video job: valida variantes, sube el video
    a Storage, crea el registro en DB con estado='pending' y encola el job.

    Args:
        video: Archivo de video subido por el usuario.
        titulo: Título descriptivo del job.
        variantes_raw: JSON string con la lista de VarianteConfig.
        background_tasks: Inyectado por FastAPI para ejecutar run_video_job en background.
        current_user: Dict del usuario autenticado (del JWT).

    Returns:
        VideoJobResponse con estado='pending'.

    Raises:
        AppError: VALIDATION_ERROR (400) si variantes_raw no es JSON válido
                  o no cumple el esquema VarianteConfig.
    """
    try:
        variantes = [VarianteConfig(**v) for v in json.loads(variantes_raw)]
    except Exception:
        raise AppError("Variantes inválidas.", ErrorCode.VALIDATION_ERROR, 400)

    video_bytes = await video.read()
    content_type = video.content_type or "application/octet-stream"
    video_input_url = _upload_video(video_bytes, video.filename or "video", content_type)

    parametros = {"variantes": [v.model_dump() for v in variantes]}
    job = create_video_job(current_user["sub"], titulo, video_input_url, parametros)

    background_tasks.add_task(run_video_job, job["id"])
    return VideoJobResponse(**job)


def list_jobs(current_user: dict) -> list[VideoJobResponse]:
    """
    Retorna el historial de video jobs del usuario autenticado.

    Args:
        current_user: Dict del usuario autenticado (del JWT).

    Returns:
        Lista de VideoJobResponse ordenada por creado_en DESC.
    """
    return [VideoJobResponse(**j) for j in list_video_jobs(current_user["sub"])]


def get_job(job_id: str, current_user: dict) -> VideoJobResponse:
    """
    Retorna un video job verificando ownership. Devuelve 404 si no existe
    o si el job no pertenece al usuario — nunca 403 (SEGURIDAD 2.4).

    Args:
        job_id: UUID del job a buscar.
        current_user: Dict del usuario autenticado (del JWT).

    Returns:
        VideoJobResponse del job solicitado.

    Raises:
        AppError: NOT_FOUND (404) si no existe o el usuario no tiene acceso.
    """
    return VideoJobResponse(**get_video_job(job_id, current_user["sub"]))
