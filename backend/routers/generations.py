from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from controllers import generation_controller
from middleware.auth import get_current_user
from schemas.generation import (
    AudienceEnum, EstiloImagenEnum, GenerationResponse, OutputEnum,
    TemplateEnum, TemaVisualEnum, ToneEnum,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=GenerationResponse, status_code=202)
@limiter.limit("20/minute")
async def create_generation(
    request: Request,
    background_tasks: BackgroundTasks,
    archivos: list[UploadFile] = File(...),
    objetivo: str = Form(...),
    informacion_adicional: Optional[str] = Form(default=None),
    template: TemplateEnum = Form(...),
    tono: ToneEnum = Form(...),
    audiencia: AudienceEnum = Form(...),
    output: OutputEnum = Form(default=OutputEnum.ambos),
    logo: Optional[UploadFile] = File(default=None),
    usar_imagenes_documento: bool = Form(default=False),
    tema_visual: TemaVisualEnum = Form(default=TemaVisualEnum.minimalist),
    estilo_imagen: EstiloImagenEnum = Form(default=EstiloImagenEnum.aiGenerated),
    paleta_colores: str = Form(default=""),
    cantidad_slides: int = Form(default=10, ge=5, le=20),
    current_user: dict = Depends(get_current_user),
) -> GenerationResponse:
    return await generation_controller.start_generation(
        background_tasks, archivos, objetivo, informacion_adicional,
        template, tono, audiencia, output, logo, current_user,
        usar_imagenes_documento, tema_visual, estilo_imagen, paleta_colores, cantidad_slides,
    )


@router.get("/", response_model=list[GenerationResponse])
def list_generations(
    current_user: dict = Depends(get_current_user),
) -> list[GenerationResponse]:
    return generation_controller.list_generations(current_user)


@router.get("/{generation_id}", response_model=GenerationResponse)
def get_generation(
    generation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> GenerationResponse:
    return generation_controller.get_generation(str(generation_id), current_user)
