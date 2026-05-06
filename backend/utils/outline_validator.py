from utils.errors import AppError, ErrorCode

_VALID_TYPES = {"portada", "contenido", "destacado", "cierre"}


def validate_outline(outline: dict) -> None:
    titulo = outline.get("titulo_presentacion")
    if not isinstance(titulo, str) or not titulo:
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    slides = outline.get("slides")
    if not isinstance(slides, list) or not (5 <= len(slides) <= 12):
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    for slide in slides:
        if not all(k in slide for k in ("tipo", "titulo", "contenido")):
            raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
        if slide["tipo"] not in _VALID_TYPES:
            raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    if slides[0]["tipo"] != "portada" or slides[-1]["tipo"] != "cierre":
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
