from integrations.gamma_client import publish_to_gamma
from integrations.supabase_client import get_supabase
from repositories import generation_repo
from services.ai_service import build_prompt, generate_outline
from services.pptx_service import generate_pptx
from utils.logger import log

_PPTX_BUCKET = "pptx-generados"


def _upload_pptx(generation_id: str, pptx_bytes: bytes) -> str:
    """
    Sube los bytes del PPTX al bucket de Supabase Storage y retorna la URL pública.

    Args:
        generation_id: UUID usado como nombre de archivo ({generation_id}.pptx).
        pptx_bytes: Contenido binario del archivo PPTX.

    Returns:
        URL pública del archivo en Supabase Storage.
    """
    path = f"{generation_id}.pptx"
    storage = get_supabase().storage.from_(_PPTX_BUCKET)
    storage.upload(
        path=path,
        file=pptx_bytes,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        },
    )
    return storage.get_public_url(path)


def run_generation(
    generation_id: str,
    texto_extraido: str,
    objetivo: str,
    informacion_adicional: str | None,
    template: str,
    tono: str,
    audiencia: str,
) -> None:
    """
    Orquesta el pipeline completo de generación de presentaciones.

    Ejecuta en orden: build_prompt → generate_outline → generate_pptx →
    Supabase Storage upload → Gamma publish → DB update_resultado.

    Si cualquier paso falla, registra estado='error' en la DB y loguea con
    log.error. No relanza la excepción — el pipeline corre en background.

    Args:
        generation_id: UUID de la generación ya insertada con estado='procesando'.
        texto_extraido: Texto concatenado de todos los archivos fuente.
        objetivo: Objetivo declarado de la presentación.
        informacion_adicional: Contexto adicional del usuario (puede ser None).
        template: Nombre del template PPTX. Ver TemplateEnum en schemas/generation.py.
        tono: Tono de la presentación. Ver ToneEnum.
        audiencia: Audiencia objetivo. Ver AudienceEnum.
    """
    try:
        prompt = build_prompt(texto_extraido, objetivo, informacion_adicional, template, tono, audiencia)
        outline = generate_outline(prompt)
        pptx_bytes = generate_pptx(outline, template)
        pptx_url = _upload_pptx(generation_id, pptx_bytes)
        gamma_url = publish_to_gamma(outline)
        generation_repo.update_resultado(
            generation_id, pptx_url, gamma_url, len(outline["slides"]), outline
        )
        log.info(f"generation.completed | id={generation_id}")
    except Exception as exc:
        generation_repo.update_error(generation_id)
        log.error(f"generation.failed | id={generation_id} | error={exc}")
