from __future__ import annotations

from integrations.supabase_client import get_supabase

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
