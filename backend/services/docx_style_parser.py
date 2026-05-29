from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

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
