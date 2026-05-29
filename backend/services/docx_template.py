from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

from docx import Document
from docx.shared import Cm, Pt, RGBColor

from utils.logger import log
from services.docx_style_parser import (
    _FONT, _C_TITULO, _C_SECCION, _C_CUERPO, _MARGIN, _SIZE_H1, _SIZE_H2,
    _SIZE_BODY, _SPACE_BEFORE_H, _SPACE_AFTER_B, _LINE_SPACING,
    _NS_A, _NS_WP, _parse_theme_color, _style_attr
)


def _extract_from_document_styles(doc, style: dict) -> None:
    """Extrae estilos directamente del documento DOCX."""
    for sname in ("Normal", "Default Paragraph Font"):
        fn = _style_attr(doc, sname, lambda s: s.font.name)
        if fn:
            style["font"] = fn
            break
    for key, sname in (("size_heading1", "Heading 1"),
                       ("size_heading2", "Heading 2"),
                       ("size_body", "Normal")):
        size = _style_attr(doc, sname, lambda s: s.font.size)
        if size is not None:
            style[key] = size
    for key, sname in (("color_titulo", "Heading 1"),
                       ("color_seccion", "Heading 2"),
                       ("color_cuerpo", "Normal")):
        c = _style_attr(doc, sname, lambda s: s.font.color.rgb)
        if c is not None:
            style[key] = c
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
    sb = _style_attr(doc, "Heading 2", lambda s: s.paragraph_format.space_before)
    if sb is not None:
        style["space_before_heading"] = sb
    sa = _style_attr(doc, "Normal", lambda s: s.paragraph_format.space_after)
    if sa is not None:
        style["space_after_body"] = sa
    ls = _style_attr(doc, "Normal", lambda s: s.paragraph_format.line_spacing)
    if ls is not None:
        style["line_spacing"] = ls
    try:
        hdr_el = doc.sections[0].header._element
        if (hdr_el.find(f".//{{{_NS_WP}}}inline") is not None
                or hdr_el.find(f".//{{{_NS_WP}}}anchor") is not None):
            style["header_element"] = deepcopy(hdr_el)
    except Exception:
        pass


def _extract_from_theme_xml(plantilla_bytes: bytes, style: dict) -> None:
    """Extrae colores y fuente del tema XML dentro del DOCX."""
    try:
        with zipfile.ZipFile(BytesIO(plantilla_bytes)) as zf:
            if "word/theme/theme1.xml" not in zf.namelist():
                return
            root = ET.fromstring(zf.read("word/theme/theme1.xml"))
            clr_scheme = root.find(f".//{{{_NS_A}}}clrScheme")
            if clr_scheme is not None:
                if style["color_titulo"] is _C_TITULO:
                    dk1 = clr_scheme.find(f"{{{_NS_A}}}dk1")
                    if dk1 is not None and (c := _parse_theme_color(dk1)):
                        style["color_titulo"] = c
                if style["color_seccion"] is _C_SECCION:
                    dk2 = clr_scheme.find(f"{{{_NS_A}}}dk2")
                    if dk2 is not None and (c := _parse_theme_color(dk2)):
                        style["color_seccion"] = c
                if style["color_cuerpo"] is _C_CUERPO:
                    c_body = _parse_theme_color(clr_scheme.find(f"{{{_NS_A}}}dk1"))
                    if c_body is not None:
                        c_dk2 = _parse_theme_color(clr_scheme.find(f"{{{_NS_A}}}dk2"))
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
                            if tf and not tf.startswith("+"):
                                style["font"] = tf
    except Exception as e:
        log.debug("Error leyendo tema DOCX", extra={"error": str(e)})


def extract_template_style(plantilla_bytes: bytes | None) -> dict:
    """Extrae propiedades estéticas de un DOCX plantilla.

    Estrategia: estilos del documento primero, theme XML como fallback,
    defaults hardcodeados como último recurso.

    Returns:
        Dict con font, colores, márgenes, tamaños, espaciado y header_element.
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
        _extract_from_document_styles(doc, style)
        _extract_from_theme_xml(plantilla_bytes, style)
    except Exception:
        pass
    return style
