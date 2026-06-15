"""Motor de layouts PPTX — layouts base (portada, contenido, destacado, cierre) y
registro BUILDERS de los 8 layouts.

Implementación única compartida por todos los templates. La geometría viene de
pptx_geometry.LAYOUTS (compartida); el color/fuente, solo de tpl.TEMPLATE (tokens).
pptx_service consume BUILDERS y pasa el módulo del template activo como `tpl`.
"""
from __future__ import annotations

from pptx.util import Inches

from services.pptx_geometry import _BULLET_MAX_SLOT, _H, _W, LAYOUTS
from services.pptx_layouts_extra import (
    build_cards_3,
    build_split_2col,
    build_steps,
    build_timeline,
)
from utils.pptx_helpers import (
    _add_textbox_italic,
    _insert_image,
    _titulo_font_size,
    _titulo_font_size_portada,
    add_rect,
    add_textbox,
    set_shape_text,
    set_slide_background,
)


def build_portada(slide, data: dict, tpl) -> None:
    """Portada: título 2.8" → línea accent 3.7" → subtítulo italic 3.95"."""
    T, L = tpl.TEMPLATE, LAYOUTS["portada"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_rect(slide, Inches(0), _H - L["banda_bottom_height"], _W, L["banda_bottom_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size_portada(data["titulo"]), T["text"], bold=True)
    ls = L["linea_sep"]
    add_rect(slide, ls["left"], Inches(3.7), ls["width"], ls["height"], T["accent"])
    subtitulo = str(data.get("contenido", ""))
    if subtitulo:
        sub_l = L["subtitulo"]
        _add_textbox_italic(
            slide,
            {"left": sub_l["left"], "top": Inches(3.95), "width": sub_l["width"], "height": sub_l["height"]},
            subtitulo, T["font_body"], 18, T["accent"],
        )


def build_contenido(slide, data: dict, tpl, imagen=None) -> None:
    """Contenido: banda top accent, título + línea, bullets con dot accent."""
    T, L = tpl.TEMPLATE, LAYOUTS["contenido"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True, auto_size=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    bullets = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    ds = L["bullet_dot_size"]
    bullet_width = Inches(6.5) if imagen else Inches(11.8)
    n = len(bullets[:5])
    available = _H - Inches(1.6) - Inches(0.3)
    slot_h = min(_BULLET_MAX_SLOT, available / n)
    bloque_h = n * slot_h
    bullets_start = Inches(1.6) + (available - bloque_h) / 2
    for i, bullet in enumerate(bullets[:5]):
        top = bullets_start + i * slot_h
        add_rect(slide, Inches(0.6), top + Inches(0.18), ds, ds, T["accent"])
        add_textbox(
            slide,
            {"left": Inches(0.85), "top": top, "width": bullet_width, "height": slot_h},
            bullet, T["font_body"], T["font_size_body"], T["text_secondary"],
            auto_size=True,
        )
    if imagen:
        _insert_image(slide, imagen)


def build_destacado(slide, data: dict, tpl, imagen=None) -> None:
    """Destacado: banda top, título + línea, caja surface con borde accent."""
    T, L = tpl.TEMPLATE, LAYOUTS["destacado"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    panel_width = Inches(7.0) if imagen else Inches(12.5)
    box = add_rect(slide, Inches(0.4), Inches(1.3), panel_width, Inches(5.8), T["surface"])
    set_shape_text(box, str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["text"])
    add_rect(slide, Inches(0.4), Inches(1.3), panel_width, Inches(0.04), T["accent"])
    if imagen:
        _insert_image(slide, imagen)


def build_cierre(slide, data: dict, tpl) -> None:
    """Cierre: título, línea a titulo_top+0.9", contenido a titulo_top+1.15"."""
    T, L = tpl.TEMPLATE, LAYOUTS["cierre"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, Inches(0.08), T["accent"])
    add_rect(slide, Inches(0), _H - Inches(0.08), _W, Inches(0.08), T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size_portada(data["titulo"]), T["text"], bold=True)
    titulo_top = L["titulo"]["top"]
    add_rect(slide, Inches(0.6), titulo_top + Inches(0.9), Inches(3.0), Inches(0.04), T["accent"])
    contenido = data.get("contenido")
    if contenido and str(contenido).strip():
        add_textbox(
            slide,
            {"left": Inches(0.6), "top": titulo_top + Inches(1.15), "width": Inches(10.0), "height": Inches(1.5)},
            str(contenido), T["font_body"], 18, T["text_secondary"],
        )


# Registro único: tipo de slide → función del motor. Los 4 nuevos vienen de
# pptx_layouts_extra; todos comparten geometría y leen color de tpl.TEMPLATE.
BUILDERS = {
    "portada": build_portada,
    "contenido": build_contenido,
    "destacado": build_destacado,
    "cierre": build_cierre,
    "cards_3": build_cards_3,
    "timeline": build_timeline,
    "split_2col": build_split_2col,
    "steps": build_steps,
}
