from __future__ import annotations

import math

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
    cantidad_slides = cantidad_slides or 10
    tope = math.ceil(cantidad_slides * 1.5)
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
        "- Inicia SIEMPRE con portada, finaliza SIEMPRE con cierre. Mínimo 5 slides.\n"
        "- COBERTURA OBLIGATORIA: toda sección numerada del cuerpo (1., 2., 3., …) debe estar representada en al menos una slide. Si el contenido fuente incluye un bloque [TABLAS DEL DOCUMENTO] (celdas detectadas de tablas que estaban como imagen, una por línea), TODO dato nombrado de esas celdas —cada proyecto/área, rol, estado y responsable— debe aparecer en al menos una slide; usá ese texto como fuente primaria y las imágenes solo para desambiguar. Podés agrupar varias secciones o entidades en una misma slide, pero ninguna entidad nombrada puede desaparecer.\n"
        f"- Apuntá a {cantidad_slides} slides (objetivo, no techo). Si la cobertura completa no entra, podés extender hasta {tope}. Priorizá cobertura sobre el límite, pero agrupá de forma inteligente para acercarte al objetivo.\n"
        "- Preservás todos los datos concretos: fechas, nombres propios, estados, responsables. No generalizás ni omitís información específica. No agregues contenido que no esté en el fuente.\n"
        "- Solo omití una slide si quedaría vacía o sin contenido real — nunca para descartar una sección o fila del documento.\n"
        "- AUTOVERIFICACIÓN: antes de escribir el JSON, listá internamente cada sección numerada y, si hay bloque [TABLAS DEL DOCUMENTO], recorré sus celdas y confirmá que cada entidad nombrada (proyectos/áreas, roles, responsables) aparece en al menos una slide. NO cuentes 'filas exactas' (el bloque lista celdas, no filas): el objetivo es no omitir ninguna entidad nombrada.\n"
        "\n"
        "TIPOS DE SLIDE DISPONIBLES:\n"
        "\n"
        "1. portada — solo uno, siempre primero.\n"
        "   contenido: str (subtítulo descriptivo)\n"
        "\n"
        "2. contenido — lista de bullets informativos.\n"
        "   contenido: list[str] de máximo 5 bullets.\n"
        "   Usarlo para: texto narrativo, listas de iniciativas, puntos de análisis.\n"
        "\n"
        "3. timeline — secuencia de hitos con fecha y estado.\n"
        '   contenido: list de exactamente 2 o 3 objetos:\n'
        '   [{"fecha": "str", "descripcion": "str", "estado": "completado|en_curso|proyectado"}]\n'
        "   footer: str (objetivo o conclusión, opcional)\n"
        "   Usarlo cuando hay: fechas de hitos, cronogramas, fases con estado.\n"
        "   REGLA: si hay 2 o 3 elementos con fecha → SIEMPRE usar timeline.\n"
        "\n"
        "4. cards_3 — exactamente 3 elementos comparables en paralelo.\n"
        '   contenido: list de exactamente 3 objetos:\n'
        '   [{"num": "01", "titulo": "str", "descripcion": "str"}]\n'
        "   Usarlo cuando hay: 3 ejes, 3 pilares, 3 dimensiones, 3 áreas temáticas.\n"
        "   REGLA: si hay exactamente 3 elementos del mismo tipo → SIEMPRE usar cards_3.\n"
        "\n"
        "5. steps — pasos numerados de un proceso.\n"
        '   contenido: list de 2 a 5 objetos:\n'
        '   [{"num": "1", "titulo": "str", "descripcion": "str"}]\n'
        "   Usarlo cuando hay: etapas de implementación, fases de un proceso,\n"
        "   pasos secuenciales con estado (completado/en curso/pendiente).\n"
        "\n"
        "6. split_2col — exactamente 2 elementos en paralelo.\n"
        '   contenido: list de exactamente 2 objetos:\n'
        '   [{"titulo": "str", "descripcion": "str"}]\n'
        "   footer: str (nota al pie, opcional)\n"
        "   Usarlo cuando hay: 2 iniciativas, 2 opciones, 2 propuestas.\n"
        "   REGLA: si hay exactamente 2 elementos del mismo tipo → SIEMPRE usar split_2col.\n"
        "\n"
        "7. destacado — un mensaje o concepto central.\n"
        "   contenido: str (texto del panel, máximo 2 oraciones)\n"
        "   Usarlo para: logro clave, dato impactante, mensaje principal.\n"
        "\n"
        "8. cierre — solo uno, siempre último.\n"
        "   contenido: str (mensaje de cierre o próximos pasos en una oración)\n"
        "\n"
        "REGLAS DE SELECCIÓN DE LAYOUT:\n"
        "- 3 elementos comparables → cards_3 (NO contenido con bullets)\n"
        "- 2 elementos en paralelo → split_2col (NO contenido con bullets)\n"
        "- Hitos con fechas → timeline (NO contenido con bullets)\n"
        "- Pasos de proceso → steps (NO contenido con bullets)\n"
        "- Todo lo demás → contenido\n"
        "\n"
        f"{bloque_imagenes}\n"
        "## OUTPUT REQUERIDO\n"
        "Respondé SOLO con JSON válido, sin texto ni markdown adicional:\n"
        "{\n"
        '  "titulo_presentacion": "str",\n'
        '  "slides": [\n'
        "    {\n"
        '      "tipo": "portada|contenido|timeline|cards_3|steps|split_2col|destacado|cierre",\n'
        '      "titulo": "str",\n'
        '      "contenido": "ver estructura según tipo arriba",\n'
        '      "footer": "str (opcional, solo en timeline y split_2col)",\n'
        '      "imagen_idx": "int (opcional, solo en contenido y destacado)"\n'
        "    }\n"
        "  ]\n"
        "}"
    )
