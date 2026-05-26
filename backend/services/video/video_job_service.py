from __future__ import annotations

from utils.logger import log


def run_video_job(job_id: str) -> None:
    """
    Punto de entrada del pipeline de procesamiento de video.

    Fase 1 — stub: registra el job como encolado y retorna.
    El worker real (FFmpeg + AWS) se conecta en Fase 2.

    Args:
        job_id: UUID del video job a procesar.
    """
    log.info(f"video_job.queued | id={job_id}")
