from __future__ import annotations

import math
import re
import unicodedata

from utils.errors import AppError, ErrorCode

_VALID_TYPES = {"portada", "contenido", "timeline", "cards_3", "steps", "split_2col", "destacado", "cierre"}

# Encabezado numerado al inicio de línea: '1. Título', '2.1) Título'.
# Exige mayúscula/dígito inicial y título corto (≤70) para no capturar
# enumeraciones dentro de párrafos (ej. '1. comprá leche').
_SECTION_RE = re.compile(r"^[ \t]*\d+(?:\.\d+)*[.)]\s+([A-ZÁÉÍÓÚÑ0-9].{2,70}?)\s*$", re.MULTILINE)
_STOPWORDS = {"de", "la", "el", "los", "las", "y", "del", "en", "para", "con", "por", "un", "una", "al", "su", "sus"}


def validate_outline(outline: dict, cantidad_slides: int | None = None) -> None:
    if cantidad_slides is None:
        cantidad_slides = 10
    limite = math.ceil(cantidad_slides * 1.5)
    titulo = outline.get("titulo_presentacion")
    if not isinstance(titulo, str) or not titulo:
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    slides = outline.get("slides")
    if not isinstance(slides, list) or not (5 <= len(slides) <= limite):
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    for slide in slides:
        if not all(k in slide for k in ("tipo", "titulo", "contenido")):
            raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
        if slide["tipo"] not in _VALID_TYPES:
            raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
        if "imagen_idx" in slide and not isinstance(slide["imagen_idx"], (int, type(None))):
            raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)
    if slides[0]["tipo"] != "portada" or slides[-1]["tipo"] != "cierre":
        raise AppError("Outline inválido", ErrorCode.GENERATION_FAILED, 503)


def _outline_text(outline: dict) -> str:
    """Concatena en minúsculas todo el texto del outline (títulos, contenidos, footers)."""
    partes: list[str] = []
    for slide in outline.get("slides", []):
        partes.append(str(slide.get("titulo", "")))
        if isinstance(slide.get("footer"), str):
            partes.append(slide["footer"])
        cont = slide.get("contenido")
        if isinstance(cont, str):
            partes.append(cont)
        elif isinstance(cont, list):
            for item in cont:
                if isinstance(item, str):
                    partes.append(item)
                elif isinstance(item, dict):
                    partes.extend(str(v) for v in item.values())
    return " ".join(partes).lower()


def check_section_coverage(texto_extraido: str, outline: dict) -> list[str]:
    """
    Detecta secciones numeradas del cuerpo no representadas en el outline (modo observación).

    Extrae encabezados tipo '1. Título' / '2.1) Título' al inicio de línea y marca una
    sección como faltante solo cuando NINGUNA de sus palabras clave (≥4 letras, sin
    stopwords) aparece en el texto del outline. Es deliberadamente conservador: apunta
    al modo de fallo real (sección entera omitida → cero solapamiento de vocabulario) y
    evita falsos positivos cuando el outline reformula el título y solo comparte parte
    de las palabras. Contrapartida: puede no detectar omisiones parciales o secciones
    cuyo título comparte una palabra común con otra parte del outline.
    NO valida filas de tablas (el texto EMF llega plano y sin acentos, ver
    image_extraction_service).

    Args:
        texto_extraido: Texto del cuerpo del documento fuente.
        outline: Outline JSON ya generado y validado.

    Returns:
        Lista de títulos de secciones no representadas. Vacía si la cobertura es completa.
    """
    outline_txt = _outline_text(outline)
    faltantes: list[str] = []
    for titulo in _SECTION_RE.findall(texto_extraido):
        titulo = titulo.strip()
        keywords = [w for w in re.findall(r"[a-záéíóúñ]+", titulo.lower())
                    if len(w) >= 4 and w not in _STOPWORDS]
        if not keywords:
            continue
        if not any(w in outline_txt for w in keywords):
            faltantes.append(titulo)
    return faltantes


# Cabeceras genéricas de tabla y ruido de fuente: no son entidades a cubrir.
_TABLE_STOPWORDS = {
    "proyecto", "area", "proyecto / area", "rol", "estado", "estado actual",
    "vacantes", "proximos pasos", "observaciones", "proceso", "descripcion",
    "capacitacion", "destinatarios", "responsable", "referente",
    "responsable / referente", "calibri",
}


def _normalizar(s: str) -> str:
    """Minúsculas sin acentos (NFKD) para comparación tolerante."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def check_table_coverage(emf_text: str, outline: dict) -> list[str]:
    """
    Detecta entidades nombradas de tablas EMF no representadas en el outline (modo observación).

    El bloque EMF lista CELDAS detectadas (encabezado '[TABLA: ...]' + una celda por
    línea), no filas exactas, así que esto es mitigación fuerte, no garantía dura.
    Toma como entidad candidata las celdas cortas y capitalizadas (≤3 palabras): nombres
    de proyecto/área, roles y responsables (Cross, Paysandú, Datos, Analista de Procesos,
    Cristina Joachim). Descarta cabeceras genéricas vía _TABLE_STOPWORDS.

    El matching es TOLERANTE (no igualdad estricta): por el ruido residual del extractor
    (ej. 'Datosl', 'No iniciadah') compara la celda normalizada —y su versión sin el
    último carácter— como substring del outline. Así 'Datosl' matchea con 'Datos' del
    outline sin generar falso positivo.

    Args:
        emf_text: Texto estructurado crudo de las tablas EMF (sin sanitizar).
        outline: Outline JSON ya generado y validado.

    Returns:
        Lista de celdas (entidades nombradas) no representadas. Vacía si la cobertura
        es completa. Puede sub/sobre-reportar: no reemplaza la revisión humana.
    """
    outline_txt = _normalizar(_outline_text(outline))
    faltantes: list[str] = []
    vistos: set[str] = set()
    for linea in emf_text.splitlines():
        celda = linea.strip()
        if not celda or celda.startswith("[TABLA"):
            continue
        if not celda[0].isupper() or len(celda.split()) > 3:
            continue
        norm = _normalizar(celda)
        if len(norm) < 3 or norm in _TABLE_STOPWORDS or norm in vistos:
            continue
        vistos.add(norm)
        if norm in outline_txt or (len(norm) >= 4 and norm[:-1] in outline_txt):
            continue
        faltantes.append(celda)
    return faltantes
