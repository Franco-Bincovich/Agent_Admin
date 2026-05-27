from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

from docx import Document
from docx.shared import Cm, Pt, RGBColor

from utils.logger import log

_FONT = "Calibri"
_C_TITULO = RGBColor(0x1E, 0x3A, 0x5F)   # #1E3A5F — título del documento
_C_SECCION = RGBColor(0x2E, 0x6D, 0xA4)  # #2E6DA4 — nombre de sección
_C_CUERPO = RGBColor(0x1A, 0x1A, 0x1A)   # #1A1A1A — cuerpo de texto
_MARGIN = Cm(2.5)
_SIZE_H1 = Pt(16)
_SIZE_H2 = Pt(13)
_SIZE_BODY = Pt(11)
_SPACE_BEFORE_H = Pt(12)
_SPACE_AFTER_B = Pt(8)
_LINE_SPACING = 1.15

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


def _style_attr(doc, style_name: str, getter):
    """Lee un atributo de un estilo del documento; retorna None si el estilo no existe o el atributo no está seteado."""
    try:
        return getter(doc.styles[style_name])
    except Exception:
        return None


def extract_template_style(plantilla_bytes: bytes | None) -> dict:
    """Extrae propiedades estéticas reales de un DOCX plantilla.

    Estrategia por propiedad: estilos del documento primero, theme XML como
    fallback, defaults hardcodeados como último recurso. Devuelve fallbacks
    completos si plantilla_bytes es None o si la lectura falla.

    Returns:
        Dict con claves font, color_titulo, color_seccion, color_cuerpo,
        margin, top_margin, bottom_margin, size_heading1, size_heading2,
        size_body, space_before_heading, space_after_body, line_spacing,
        header_element.
    """
    style: dict = {
        "font": _FONT,
        "color_titulo": _C_TITULO,
        "color_seccion": _C_SECCION,
        "color_cuerpo": _C_CUERPO,
        "margin": _MARGIN,
        "top_margin": _MARGIN,
        "bottom_margin": _MARGIN,
        "size_heading1": _SIZE_H1,
        "size_heading2": _SIZE_H2,
        "size_body": _SIZE_BODY,
        "space_before_heading": _SPACE_BEFORE_H,
        "space_after_body": _SPACE_AFTER_B,
        "line_spacing": _LINE_SPACING,
        "header_element": None,
    }

    if not plantilla_bytes:
        return style

    try:
        doc = Document(BytesIO(plantilla_bytes))
    except Exception:
        return style

    # 1. Fuente: Normal → Default Paragraph Font (theme y "Calibri" quedan como fallback)
    for sname in ("Normal", "Default Paragraph Font"):
        fn = _style_attr(doc, sname, lambda s: s.font.name)
        if fn:
            style["font"] = fn
            break

    # 2. Tamaños de fuente desde estilos
    for key, sname in (("size_heading1", "Heading 1"),
                       ("size_heading2", "Heading 2"),
                       ("size_body", "Normal")):
        size = _style_attr(doc, sname, lambda s: s.font.size)
        if size is not None:
            style[key] = size

    # 3. Colores desde estilos (antes del fallback al theme)
    for key, sname in (("color_titulo", "Heading 1"),
                       ("color_seccion", "Heading 2"),
                       ("color_cuerpo", "Normal")):
        c = _style_attr(doc, sname, lambda s: s.font.color.rgb)
        if c is not None:
            style[key] = c

    # 4. Márgenes desde la primera sección
    try:
        section = doc.sections[0]
        for key, attr in (("margin", "left_margin"),
                          ("top_margin", "top_margin"),
                          ("bottom_margin", "bottom_margin")):
            val = getattr(section, attr, None)
            if val and val > 0:
                style[key] = val
    except Exception:
        pass

    # 5. Espaciado e interlineado desde estilos
    sb = _style_attr(doc, "Heading 2", lambda s: s.paragraph_format.space_before)
    if sb is not None:
        style["space_before_heading"] = sb
    sa = _style_attr(doc, "Normal", lambda s: s.paragraph_format.space_after)
    if sa is not None:
        style["space_after_body"] = sa
    ls = _style_attr(doc, "Normal", lambda s: s.paragraph_format.line_spacing)
    if ls is not None:
        style["line_spacing"] = ls

    # 6. Header con imágenes (wp:inline o wp:anchor)
    try:
        hdr_el = doc.sections[0].header._element
        if (hdr_el.find(f".//{{{_NS_WP}}}inline") is not None
                or hdr_el.find(f".//{{{_NS_WP}}}anchor") is not None):
            style["header_element"] = deepcopy(hdr_el)
    except Exception:
        pass

    # 7. Fallback al theme XML para colores y fuente cuando los estilos no aportaron
    try:
        with zipfile.ZipFile(BytesIO(plantilla_bytes)) as zf:
            if "word/theme/theme1.xml" in zf.namelist():
                root = ET.fromstring(zf.read("word/theme/theme1.xml"))

                clr_scheme = root.find(f".//{{{_NS_A}}}clrScheme")
                if clr_scheme is not None:
                    if style["color_titulo"] is _C_TITULO:
                        dk1 = clr_scheme.find(f"{{{_NS_A}}}dk1")
                        if dk1 is not None:
                            c = _parse_theme_color(dk1)
                            if c:
                                style["color_titulo"] = c
                    if style["color_seccion"] is _C_SECCION:
                        dk2 = clr_scheme.find(f"{{{_NS_A}}}dk2")
                        if dk2 is not None:
                            c = _parse_theme_color(dk2)
                            if c:
                                style["color_seccion"] = c
                    if style["color_cuerpo"] is _C_CUERPO:
                        c_body = None
                        dk1 = clr_scheme.find(f"{{{_NS_A}}}dk1")
                        if dk1 is not None:
                            c_body = _parse_theme_color(dk1)
                        if c_body is not None:
                            dk2 = clr_scheme.find(f"{{{_NS_A}}}dk2")
                            if dk2 is not None:
                                c_dk2 = _parse_theme_color(dk2)
                                # Luminancia relativa (WCAG 2.1): si dk2 es más oscuro que dk1, preferir dk2
                                if c_dk2 is not None and (
                                    0.2126 * c_dk2[0] + 0.7152 * c_dk2[1] + 0.0722 * c_dk2[2]
                                    < 0.2126 * c_body[0] + 0.7152 * c_body[1] + 0.0722 * c_body[2]
                                ):
                                    c_body = c_dk2
                            style["color_cuerpo"] = c_body

                if style["font"] == _FONT:
                    font_scheme = root.find(f".//{{{_NS_A}}}fontScheme")
                    if font_scheme is not None:
                        minor = font_scheme.find(f"{{{_NS_A}}}minorFont")
                        if minor is not None:
                            latin = minor.find(f"{{{_NS_A}}}latin")
                            if latin is not None:
                                tf = latin.get("typeface", "")
                                # Tokens "+mn-lt"/"+mj-lt" son referencias relativas, no nombres reales
                                if tf and not tf.startswith("+"):
                                    style["font"] = tf
    except Exception as e:
        log.debug("Error leyendo tema DOCX", extra={"error": str(e)})

    return style
