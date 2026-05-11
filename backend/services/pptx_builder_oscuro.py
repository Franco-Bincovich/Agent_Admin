from __future__ import annotations

import io

from pptx.util import Inches

from utils.pptx_helpers import add_rect, add_textbox, set_shape_text, set_slide_background

_W = Inches(13.33)
_H = Inches(7.5)


def build_portada(slide, data: dict, tpl) -> None:
    """Portada ejecutivo_oscuro: fondo oscuro, bandas accent, panel deco derecho, título izquierda."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["portada"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent_color"])
    add_rect(slide, Inches(0), _H - L["banda_bottom_height"], _W, L["banda_bottom_height"], T["accent_color"])
    pd = L["panel_deco"]
    add_rect(slide, pd["left"], pd["top"], pd["width"], pd["height"], T["panel_color"])
    pb = L["panel_borde"]
    add_rect(slide, pb["left"], pb["top"], pb["width"], pb["height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], T["text_color"], bold=True)
    ls = L["linea_sep"]
    add_rect(slide, ls["left"], ls["top"], ls["width"], ls["height"], T["accent_color"])
    add_textbox(slide, L["subtitulo"], str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["accent_color"])


def build_contenido(slide, data: dict, tpl, imagen=None) -> None:
    """Contenido ejecutivo_oscuro: fondo oscuro, banda top accent, título + línea, bullets con dot accent."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["contenido"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], T["text_color"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent_color"])
    bullets = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    ds = L["bullet_dot_size"]
    for i, bullet in enumerate(bullets[:5]):
        top = L["bullets_start_y"] + i * L["bullet_height"]
        add_rect(slide, Inches(0.6), top + Inches(0.18), ds, ds, T["accent_color"])
        add_textbox(
            slide,
            {"left": Inches(0.85), "top": top, "width": Inches(12.0), "height": L["bullet_height"]},
            bullet, T["font_body"], T["font_size_body"], T["secondary_text"],
        )
    if imagen:
        _insert_image(slide, imagen)


def build_destacado(slide, data: dict, tpl, imagen=None) -> None:
    """Destacado ejecutivo_oscuro: banda top, título + línea, caja panel_color con borde accent."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["destacado"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], T["text_color"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent_color"])
    b = L["box"]
    box = add_rect(slide, b["left"], b["top"], b["width"], b["height"], T["panel_color"])
    set_shape_text(box, str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["text_color"])
    add_rect(slide, b["left"], b["top"], b["width"], Inches(0.04), T["accent_color"])
    if imagen:
        _insert_image(slide, imagen)


def build_cierre(slide, data: dict, tpl) -> None:
    """Cierre ejecutivo_oscuro: fondo oscuro, bandas accent, título blanco grande centrado + línea."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["cierre"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, Inches(0.08), T["accent_color"])
    add_rect(slide, Inches(0), _H - Inches(0.08), _W, Inches(0.08), T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], T["text_color"], bold=True)
    ln = L["linea"]
    add_rect(slide, ln["left"], ln["top"], ln["width"], ln["height"], T["accent_color"])


def _insert_image(slide, imagen) -> None:
    """Inserta imagen a la derecha del contenido. Falla silenciosamente."""
    try:
        _, img_bytes = imagen
        slide.shapes.add_picture(
            io.BytesIO(img_bytes),
            left=int(Inches(8.0)), top=int(Inches(1.5)), width=int(Inches(4.8)),
        )
    except Exception:
        pass
