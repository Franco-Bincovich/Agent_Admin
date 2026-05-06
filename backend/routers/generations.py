from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from controllers import generation_controller
from middleware.auth import get_current_user
from schemas.generation import AudienceEnum, GenerationResponse, OutputEnum, TemplateEnum, ToneEnum

router = APIRouter()


@router.post("/", response_model=GenerationResponse, status_code=202)
async def create_generation(
    background_tasks: BackgroundTasks,
    archivos: list[UploadFile] = File(...),
    objetivo: str = Form(...),
    informacion_adicional: str | None = Form(default=None),
    template: TemplateEnum = Form(...),
    tono: ToneEnum = Form(...),
    audiencia: AudienceEnum = Form(...),
    output: OutputEnum = Form(default=OutputEnum.ambos),
    current_user: dict = Depends(get_current_user),
) -> GenerationResponse:
    return await generation_controller.start_generation(
        background_tasks, archivos, objetivo, informacion_adicional,
        template, tono, audiencia, output, current_user,
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
