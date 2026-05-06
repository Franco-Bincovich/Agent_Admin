from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.shared import Cm, Pt, RGBColor

from utils.errors import AppError, ErrorCode
from utils.logger import log

_FONT = "Calibri"
_C_TITULO = RGBColor(0x1E, 0x3A, 0x5F)   # #1E3A5F — título del documento
_C_SECCION = RGBColor(0x2E, 0x6D, 0xA4)  # #2E6DA4 — nombre de sección
_C_CUERPO = RGBColor(0x1A, 0x1A, 0x1A)   # #1A1A1A — cuerpo de texto
_MARGIN = Cm(2.5)


def _new_doc_with_defaults() -> Document:
    """Crea un Document nuevo con márgenes de 2.5cm en todos los lados."""
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = _MARGIN
    return doc


def _style_run(run, size_pt: int, color: RGBColor, bold: bool = False) -> None:
    """Aplica fuente Calibri, tamaño en pt, color RGB y negrita a un run."""
    run.font.name = _FONT
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    run.bold = bold


def generate_docx(
    outline: dict,
    imagenes: list[tuple[str, bytes]],
    usar_imagenes: bool,
    plantilla_bytes: bytes | None,
) -> bytes:
    """
    Convierte el outline JSON de unificación en un archivo .docx descargable.

    Si plantilla_bytes no es None, lo carga como documento base respetando sus
    estilos existentes. Si es None, crea un documento nuevo con estilo ejecutivo
    por defecto: Calibri, título 24pt/#1E3A5F (negrita), nombre de sección
    16pt/#2E6DA4 (negrita) con línea separadora, cuerpo 11pt/#1A1A1A
    interlineado 1.15, márgenes 2.5cm en todos los lados.

    Para cada sección del outline agrega heading con separador, el párrafo de
    contenido, y si usar_imagenes=True llama a _insert_relevant_image (stub).

    Args:
        outline: Dict con {titulo: str, secciones: list[{nombre, contenido}]}.
        imagenes: Lista de (nombre_imagen, bytes) disponibles para inserción.
        usar_imagenes: Si True, llama a _insert_relevant_image por cada sección.
        plantilla_bytes: Bytes de un .docx base. Si None aplica estilos por defecto.

    Returns:
        Bytes del .docx generado, listos para descarga.

    Raises:
        AppError: DOCUMENTO_GENERATION_FAILED 500 si falla la generación del archivo.
    """
    try:
        if plantilla_bytes:
            doc = Document(BytesIO(plantilla_bytes))
        else:
            doc = _new_doc_with_defaults()
            p_titulo = doc.add_paragraph()
            _style_run(p_titulo.add_run(outline.get("titulo", "")), 24, _C_TITULO, bold=True)

        for seccion in outline.get("secciones", []):
            nombre = seccion.get("nombre", "")
            contenido = seccion.get("contenido", "")

            p_h = doc.add_paragraph()
            _style_run(p_h.add_run(nombre), 16, _C_SECCION, bold=True)
            doc.add_paragraph("─" * 60)

            p_b = doc.add_paragraph(contenido)
            if p_b.runs:
                _style_run(p_b.runs[0], 11, _C_CUERPO)
            p_b.paragraph_format.line_spacing = 1.15

            if usar_imagenes:
                _insert_relevant_image(doc, nombre, contenido, imagenes)

        buffer = BytesIO()
        doc.save(buffer)
        log.info(f"docx.generated | secciones={len(outline.get('secciones', []))}")
        return buffer.getvalue()

    except AppError:
        raise
    except Exception as exc:
        log.error(f"docx.generation.failed | error={exc}")
        raise AppError("Error generando el documento DOCX.", ErrorCode.DOCUMENTO_GENERATION_FAILED, 500)


def _insert_relevant_image(
    doc: Document,
    seccion_nombre: str,
    seccion_contenido: str,
    imagenes: list[tuple[str, bytes]],
) -> None:
    """
    Intenta insertar la imagen más relevante al final de la sección.

    Stub — la lógica de matching semántico entre el contenido de la sección
    y las imágenes disponibles se implementa en la siguiente fase del proyecto.
    Por ahora no inserta nada.

    Args:
        doc: Documento python-docx en construcción.
        seccion_nombre: Nombre de la sección actual.
        seccion_contenido: Texto completo de la sección actual.
        imagenes: Lista de (nombre_imagen, bytes) disponibles para inserción.
    """
    pass
