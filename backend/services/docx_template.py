from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

from docx import Document
from docx.shared import Cm, RGBColor

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
    """Extrae fuente, colores y márgenes de un DOCX plantilla; devuelve fallbacks si es None."""
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

                    try:
                        c_body = None
                        dk1 = clr_scheme.find(f"{{{_NS_A}}}dk1")
                        if dk1 is not None:
                            c_body = _parse_theme_color(dk1)
                        if c_body is not None:
                            dk2 = clr_scheme.find(f"{{{_NS_A}}}dk2")
                            if dk2 is not None:
                                c_dk2 = _parse_theme_color(dk2)
                                # Fórmula de luminancia relativa (WCAG 2.1)
                                # para determinar si el color de tema es claro
                                # u oscuro y elegir el color de texto con
                                # contraste adecuado.
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
