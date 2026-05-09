from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from utils.errors import AppError, ErrorCode
from utils.logger import log

_FONT = "Calibri"
_C_TITULO = RGBColor(0x1E, 0x3A, 0x5F)   # #1E3A5F — título del documento
_C_SECCION = RGBColor(0x2E, 0x6D, 0xA4)  # #2E6DA4 — nombre de sección
_C_CUERPO = RGBColor(0x1A, 0x1A, 0x1A)   # #1A1A1A — cuerpo de texto
_MARGIN = Cm(2.5)

_NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


def _parse_theme_color(node) -> RGBColor | None:
    """Extrae RGBColor de un nodo de color de tema: <a:srgbClr val> o <a:sysClr lastClr>."""
    srgb = node.find(f"{{{_NS_A}}}srgbClr")
    if srgb is not None:
        val = srgb.get("val", "")
        if len(val) == 6:
            try:
                return RGBColor(int(val[0:2], 16), int(val[2:4], 16), int(val[4:6], 16))
            except ValueError:
                pass
    sysclr = node.find(f"{{{_NS_A}}}sysClr")
    if sysclr is not None:
        val = sysclr.get("lastClr", "")
        if len(val) == 6:
            try:
                return RGBColor(int(val[0:2], 16), int(val[2:4], 16), int(val[4:6], 16))
            except ValueError:
                pass
    return None


def extract_template_style(plantilla_bytes: bytes | None) -> dict:
    """
    Extrae la identidad visual de una plantilla DOCX.

    Cada campo se extrae de forma independiente con su propio try/except.
    Si la extracción de un campo falla, se usa el valor hardcodeado como fallback.
    Si plantilla_bytes es None, devuelve directamente todos los fallbacks.

    Extrae en orden:
    1. Fuente: Normal style → word/theme/theme1.xml minorFont → fallback "Calibri".
    2. Colores: <a:dk1> → color_titulo, <a:dk2> → color_seccion desde clrScheme.
    3. Márgenes: sections[0].left_margin si es válido (> 0).
    4. Header: element lxml si la primera sección tiene imágenes en el header.

    Returns:
        dict con claves:
            font (str), color_titulo (RGBColor), color_seccion (RGBColor),
            color_cuerpo (RGBColor), margin (int/Emu), header_element (lxml Element | None).
    """
    style: dict = {
        "font": _FONT,
        "color_titulo": _C_TITULO,
        "color_seccion": _C_SECCION,
        "color_cuerpo": _C_CUERPO,
        "margin": _MARGIN,
        "header_element": None,
    }

    if not plantilla_bytes:
        return style

    try:
        doc = Document(BytesIO(plantilla_bytes))
    except Exception:
        return style

    # 1a. Fuente desde el estilo Normal
    try:
        font_name = doc.styles["Normal"].font.name
        if font_name:
            style["font"] = font_name
    except Exception:
        pass

    # 2. Márgenes desde la primera sección
    try:
        m = doc.sections[0].left_margin
        if m and m > 0:
            style["margin"] = m
    except Exception:
        pass

    # 3. Header con imágenes (wp:inline o wp:anchor)
    try:
        hdr_el = doc.sections[0].header._element
        has_images = (
            hdr_el.find(f".//{{{_NS_WP}}}inline") is not None
            or hdr_el.find(f".//{{{_NS_WP}}}anchor") is not None
        )
        if has_images:
            style["header_element"] = deepcopy(hdr_el)
    except Exception:
        pass

    # 4. Colores y fuente fallback desde word/theme/theme1.xml
    try:
        with zipfile.ZipFile(BytesIO(plantilla_bytes)) as zf:
            if "word/theme/theme1.xml" in zf.namelist():
                root = ET.fromstring(zf.read("word/theme/theme1.xml"))

                clr_scheme = root.find(f".//{{{_NS_A}}}clrScheme")
                if clr_scheme is not None:
                    for style_key, node_name in (("color_titulo", "dk1"), ("color_seccion", "dk2")):
                        node = clr_scheme.find(f"{{{_NS_A}}}{node_name}")
                        if node is not None:
                            c = _parse_theme_color(node)
                            if c:
                                style[style_key] = c

                    # color_cuerpo: dk1 es el color de texto primario en OOXML; si dk2 es
                    # más oscuro (menor luminosidad relativa), se prefiere para el cuerpo
                    try:
                        c_body = None
                        dk1 = clr_scheme.find(f"{{{_NS_A}}}dk1")
                        if dk1 is not None:
                            c_body = _parse_theme_color(dk1)
                        if c_body is not None:
                            dk2 = clr_scheme.find(f"{{{_NS_A}}}dk2")
                            if dk2 is not None:
                                c_dk2 = _parse_theme_color(dk2)
                                if c_dk2 is not None and (
                                    0.2126 * c_dk2[0] + 0.7152 * c_dk2[1] + 0.0722 * c_dk2[2]
                                    < 0.2126 * c_body[0] + 0.7152 * c_body[1] + 0.0722 * c_body[2]
                                ):
                                    c_body = c_dk2
                        if c_body is not None:
                            style["color_cuerpo"] = c_body
                    except Exception:
                        pass

                # 1b. Fuente del tema solo si Normal style no la aportó
                if style["font"] == _FONT:
                    font_scheme = root.find(f".//{{{_NS_A}}}fontScheme")
                    if font_scheme is not None:
                        minor = font_scheme.find(f"{{{_NS_A}}}minorFont")
                        if minor is not None:
                            latin = minor.find(f"{{{_NS_A}}}latin")
                            if latin is not None:
                                tf = latin.get("typeface", "")
                                # Los tokens "+mn-lt"/"+mj-lt" son referencias relativas, no nombres reales
                                if tf and not tf.startswith("+"):
                                    style["font"] = tf
    except Exception:
        pass

    # 4b. color_cuerpo: fallback al color del estilo Normal si el theme no lo aportó
    if style["color_cuerpo"] is _C_CUERPO:
        try:
            rgb = doc.styles["Normal"].font.color.rgb
            if rgb is not None:
                style["color_cuerpo"] = rgb
        except Exception:
            pass

    return style


def _new_doc_with_defaults(margin: int = _MARGIN) -> Document:
    """Crea un Document nuevo aplicando el margen dado en todos los lados."""
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = margin
    return doc


def _style_run(run, size_pt: int, color: RGBColor, bold: bool = False, font: str = _FONT) -> None:
    """Aplica fuente, tamaño en pt, color RGB y negrita a un run."""
    run.font.name = font
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    run.bold = bold


def _insert_logo(doc: Document, logo_bytes: bytes) -> None:
    """Inserta logo centrado al inicio del documento. No-op silencioso si falla."""
    try:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(BytesIO(logo_bytes), height=Cm(4))
        body = doc.element.body
        body.remove(p._element)
        body.insert(0, p._element)
    except Exception:
        pass


def generate_docx(
    outline: dict,
    imagenes: list[tuple[str, bytes]],
    usar_imagenes: bool,
    plantilla_bytes: bytes | None,
    logo_bytes: bytes | None = None,
) -> bytes:
    """
    Convierte el outline JSON de unificación en un archivo .docx descargable.

    Si plantilla_bytes no es None, lo carga como documento base y extrae su
    identidad visual (fuente, colores, márgenes) mediante extract_template_style.
    Si es None, aplica los valores por defecto (Calibri, paleta ejecutiva, 2.5cm).

    En ambos casos aplica la misma estructura: título, heading de sección con
    separador, cuerpo con interlineado 1.15, e imagen centrada si usar_imagenes.

    Args:
        outline: Dict con {titulo: str, secciones: list[{nombre, contenido}]}.
        imagenes: Lista de (nombre_fuente, bytes_imagen) para inserción.
        usar_imagenes: Si True inserta una imagen por sección si hay disponibles.
        plantilla_bytes: Bytes de un .docx base. Si None aplica estilos por defecto.

    Returns:
        Bytes del .docx generado, listos para descarga.

    Raises:
        AppError: DOCUMENTO_GENERATION_FAILED 500 si falla la generación del archivo.
    """
    try:
        style = extract_template_style(plantilla_bytes)
        font = style["font"]
        c_titulo = style["color_titulo"]
        c_seccion = style["color_seccion"]
        c_cuerpo = style["color_cuerpo"]
        margin = style["margin"]

        if plantilla_bytes:
            doc = Document(BytesIO(plantilla_bytes))
        else:
            doc = _new_doc_with_defaults(margin)

        if logo_bytes:
            _insert_logo(doc, logo_bytes)

        if not plantilla_bytes:
            p_titulo = doc.add_paragraph()
            _style_run(p_titulo.add_run(outline.get("titulo", "")), 24, c_titulo, bold=True, font=font)

        for sec_idx, seccion in enumerate(outline.get("secciones", [])):
            nombre = seccion.get("nombre", "")
            contenido = seccion.get("contenido", "")

            p_h = doc.add_paragraph()
            _style_run(p_h.add_run(nombre), 16, c_seccion, bold=True, font=font)
            doc.add_paragraph("─" * 60)

            p_b = doc.add_paragraph(contenido)
            if p_b.runs:
                _style_run(p_b.runs[0], 11, c_cuerpo, font=font)
            p_b.paragraph_format.line_spacing = 1.15

            if usar_imagenes:
                _insert_relevant_image(doc, nombre, contenido, imagenes, sec_idx)

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
    sec_idx: int,
) -> None:
    """
    Inserta la imagen asignada a esta sección al final de su párrafo de contenido.

    Estrategia de asignación: cada sección recibe la imagen en la posición sec_idx
    de la lista. Si hay más secciones que imágenes, las secciones sobrantes no
    reciben imagen (no se repiten). La imagen se centra horizontalmente y se escala
    al ancho del área de contenido (page_width menos márgenes). Si los bytes no
    representan un formato válido, se ignora silenciosamente.

    Args:
        doc: Documento python-docx en construcción.
        seccion_nombre: Nombre de la sección actual (no usado en matching simple).
        seccion_contenido: Texto completo de la sección actual (no usado aquí).
        imagenes: Lista de (nombre_fuente, bytes_imagen) disponibles.
        sec_idx: Índice de la sección actual en el outline.
    """
    if not imagenes or sec_idx >= len(imagenes):
        return

    _, img_bytes = imagenes[sec_idx]

    section = doc.sections[-1]
    available_width = section.page_width - section.left_margin - section.right_margin

    try:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(BytesIO(img_bytes), width=available_width)
    except Exception:
        pass
