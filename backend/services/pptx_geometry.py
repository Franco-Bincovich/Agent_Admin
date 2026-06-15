"""Geometría compartida del motor de layouts PPTX.

Posiciones, tamaños y espaciado únicos para los 8 layouts, idénticos en todos los
templates (provienen del diseño de ejecutivo_oscuro, el único completo). Lo único que
varía por template son los tokens de color/fuente del TEMPLATE; la estructura es esta.
Vive en su propio módulo para que pptx_layouts y pptx_layouts_extra lo compartan sin
import circular.
"""
from pptx.util import Inches

_W = Inches(13.33)
_H = Inches(7.5)
_BULLET_MAX_SLOT = Inches(1.3)

LAYOUTS = {
    "portada": {
        "banda_top_height": Inches(0.08),
        "banda_bottom_height": Inches(0.08),
        "subtitulo": {"left": Inches(0.6), "top": Inches(1.8), "width": Inches(8.5), "height": Inches(0.55)},
        "titulo": {"left": Inches(0.6), "top": Inches(2.8), "width": Inches(8.5), "height": Inches(1.5)},
        "linea_sep": {"left": Inches(0.6), "top": Inches(3.4), "width": Inches(3.5), "height": Inches(0.04)},
    },
    "contenido": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(1.2)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.55), "width": Inches(4.0), "height": Inches(0.04)},
        "bullets_start_y": Inches(1.75),
        "bullet_height": Inches(1.0),
        "bullet_dot_size": Inches(0.12),
    },
    "destacado": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(0.8)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.1), "width": Inches(4.0), "height": Inches(0.04)},
        "box": {"left": Inches(0.6), "top": Inches(1.5), "width": Inches(12.0), "height": Inches(4.5)},
    },
    "cierre": {
        "titulo": {"left": Inches(0.6), "top": Inches(2.8), "width": Inches(12.0), "height": Inches(1.5)},
    },
    "cards_3": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(1.2)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.1), "width": Inches(4.0), "height": Inches(0.04)},
        "card_width": Inches(3.9),
        "card_start_x": Inches(0.4),
        "card_gap": Inches(0.1),
        "card_height": Inches(3.5),
        "card_top": Inches(1.5),
    },
    "timeline": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(1.2)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.1), "width": Inches(4.0), "height": Inches(0.04)},
        "card_width": Inches(3.7),
        "card_start_x": Inches(0.5),
        "card_gap": Inches(0.3),
        "card_height": Inches(3.4),
        "card_top": Inches(1.5),
        "footer_top": Inches(5.1),
    },
    "split_2col": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(1.0)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.1), "width": Inches(4.0), "height": Inches(0.04)},
        "card_width": Inches(5.9),
        "card_left_x": Inches(0.5),
        "card_right_x": Inches(6.9),
        "card_height": Inches(2.8),
        "card_top": Inches(1.3),
        "footer_top": Inches(4.25),
    },
    "steps": {
        "banda_top_height": Inches(0.08),
        "titulo": {"left": Inches(0.6), "top": Inches(0.3), "width": Inches(12.0), "height": Inches(1.2)},
        "linea_titulo": {"left": Inches(0.6), "top": Inches(1.1), "width": Inches(4.0), "height": Inches(0.04)},
        "steps_start_y": Inches(1.35),
    },
}
