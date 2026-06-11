from __future__ import annotations

from utils.prompt_sanitizer import sanitize_for_prompt

_TONO_MAP = {
    "formal": "lenguaje neutro y preciso, sin coloquialismos",
    "institucional": "lenguaje de política pública y gestión organizacional",
    "comercial": "orientado a propuesta de valor y resultados de negocio",
    "tecnico": "terminología específica del dominio, datos y métricas",
}
_AUDIENCIA_MAP = {
    "directivos": "alto nivel, foco en decisión e impacto, sin detalle operativo",
    "equipo_interno": "foco en proceso, responsabilidades y next steps",
    "clientes": "orientado a beneficios, social proof y propuesta de valor",
    "tecnicos": "detalle de implementación, arquitectura y especificaciones",
}


def build_prompt(
    texto_extraido: str,
    objetivo: str,
    informacion_adicional: str | None,
    template: str,
    tono: str,
    audiencia: str,
    cantidad_slides: int = 10,
) -> str:
    """
    Construye el prompt de usuario con los bloques 2-6 de instrucción para Claude.

    El bloque 1 (identidad/rol) vive en _SYSTEM_PROMPT dentro de ai_service y se
    pasa siempre como parámetro system= en la llamada a la API (SEGURIDAD 6.1).
    Sanitiza texto_extraido e informacion_adicional para prevenir prompt injection.

    Args:
        texto_extraido: Texto concatenado de todos los archivos fuente.
        objetivo: Objetivo declarado de la presentación.
        informacion_adicional: Contexto adicional del usuario (puede ser None).
        template: Nombre del template PPTX.
        tono: Clave de tono. Ver _TONO_MAP.
        audiencia: Clave de audiencia. Ver _AUDIENCIA_MAP.
        cantidad_slides: Máximo de slides a generar (5 mínimo). Default 10.
        Si hay imágenes adjuntas al mensaje de Claude,
        el prompt instruye a asignarlas por contenido visual.
    """
    fuente = sanitize_for_prompt(texto_extraido)
    objetivo_clean = sanitize_for_prompt(objetivo)
    adicional = sanitize_for_prompt(informacion_adicional or "", 500)
    bloque_adicional = f"\nInformación adicional:\n{adicional}" if adicional else ""
    instruccion_tono = _TONO_MAP.get(tono, tono)
    instruccion_audiencia = _AUDIENCIA_MAP.get(audiencia, audiencia)
    bloque_imagenes = (
        "- Si recibís imágenes junto a este mensaje, "
        "analizá su contenido visual.\n"
        "- Asigná imagen_idx ÚNICAMENTE en slides de tipo "
        "'contenido' o 'destacado' — NUNCA en portada ni cierre.\n"
        "- Intentá usar TODAS las imágenes recibidas — "
        "distribuílas en los slides más relevantes según su contenido visual.\n"
        "- Si hay más imágenes que slides de tipo contenido/destacado, "
        "priorizá las más relevantes.\n"
        "- No repitas el mismo índice en más de un slide.\n"
    )
    return (
        f"## CONTENIDO FUENTE\n{fuente}{bloque_adicional}\n\n"
        f"## OBJETIVO\n{objetivo_clean}\n\n"
        "## PARÁMETROS DE DISEÑO\n"
        f"- Template: {template}\n"
        f"- Tono: {tono} — {instruccion_tono}\n"
        f"- Audiencia: {audiencia} — {instruccion_audiencia}\n\n"
        "## ESTRUCTURA DE SLIDES\n"
        "- Inicia SIEMPRE con portada, finaliza SIEMPRE con cierre.\n"
        "- Tipos de slide: portada, contenido, destacado, cierre.\n"
        f"- Mínimo 5 slides, máximo {cantidad_slides}.\n"
        "- Slide 'contenido': campo 'contenido' es list[str] de máximo 5 bullets.\n"
        "- Slide 'portada' / 'destacado' / 'cierre': campo 'contenido' es str.\n"
        "- TODOS los slides deben tener contenido sustancial — "
        "nunca dejes el campo 'contenido' vacío o como string vacío.\n"
        "- Si el documento fuente no tiene información suficiente para un slide, "
        "omití ese slide. No agregues contenido que no esté en el fuente.\n"
        f"{bloque_imagenes}\n"
        "## OUTPUT REQUERIDO\n"
        "Responde SOLO con JSON válido, sin texto ni markdown adicional:\n"
        '{"titulo_presentacion": "str", '
        '"slides": [{"tipo": "str", "titulo": "str", "contenido": "str | list[str]", "imagen_idx": "int (opcional, solo si hay imagen relevante)"}]}'
    )
