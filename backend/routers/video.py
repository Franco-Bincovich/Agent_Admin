from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers import video_controller
from middleware.auth import get_current_user
from schemas.video import VideoJobResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/jobs", response_model=VideoJobResponse, status_code=202)
@limiter.limit("20/minute")
async def create_job(
    request: Request,
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    titulo: str = Form(..., max_length=200),
    variantes: str = Form(...),
    current_user: dict = Depends(get_current_user),
) -> VideoJobResponse:
    """
    Crea un nuevo video job, sube el video a Storage y lo encola para procesamiento.

    Raises:
        400: Variantes inválidas (VALIDATION_ERROR)
        401: Token inválido o ausente (UNAUTHORIZED)
        429: Rate limit excedido (RATE_LIMIT_EXCEEDED)
    """
    return await video_controller.create_job(
        video, titulo, variantes, background_tasks, current_user,
    )


@router.get("/jobs", response_model=list[VideoJobResponse])
def list_jobs(
    current_user: dict = Depends(get_current_user),
) -> list[VideoJobResponse]:
    """
    Retorna el historial de video jobs del usuario autenticado.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
    """
    return video_controller.list_jobs(current_user)


@router.get("/jobs/{job_id}", response_model=VideoJobResponse)
def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
) -> VideoJobResponse:
    """
    Retorna un video job por ID verificando ownership.

    Raises:
        401: Token inválido o ausente (UNAUTHORIZED)
        404: Job no encontrado o sin acceso (NOT_FOUND)
    """
    return video_controller.get_job(job_id, current_user)
