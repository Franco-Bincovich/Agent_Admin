from __future__ import annotations

import io

from pptx.util import Inches

from utils.pptx_helpers import add_rect, add_textbox, set_shape_text, set_slide_background

_W = Inches(13.33)
_H = Inches(7.5)


def build_portada(slide, data: dict, tpl) -> None:
    """Portada corporativo_neutro: fondo gris claro, panel derecho navy, títulos en panel derecho."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["portada"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, L["panel_dcho_x"], Inches(0), L["panel_dcho_width"], _H, T["header_color"])
    pb = L["panel_borde"]
    add_rect(slide, pb["left"], pb["top"], pb["width"], pb["height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], "FFFFFF", bold=True)
    add_textbox(slide, L["subtitulo"], str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["secondary_text"])
    add_textbox(slide, L["descripcion"], str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["secondary_text"])
    add_textbox(slide, L["empresa_label"], data.get("empresa", ""), T["font_body"], T["font_size_body"], T["accent_color"], bold=True)


def build_contenido(slide, data: dict, tpl, imagen=None) -> None:
    """Contenido corporativo_neutro: header navy + línea accent + bullets como cards con borde accent."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["contenido"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["header_height"], T["header_color"])
    add_rect(slide, Inches(0), L["header_height"], _W, L["acento_height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], "FFFFFF", bold=True, auto_size=True)
    bullets = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    cbw = L["card_borde_width"]
    card_width = Inches(6.8) if imagen else Inches(12.3)
    bullet_width = Inches(6.2) if imagen else Inches(11.5)
    bullets_start = L["bullets_start_y"]
    n = len(bullets[:5])
    bullet_h = max(Inches(0.8), (_H - bullets_start - Inches(0.3)) / n)
    for i, bullet in enumerate(bullets[:5]):
        top = bullets_start + i * bullet_h
        add_rect(slide, Inches(0.5), top, card_width, bullet_h, T["card_color"])
        add_rect(slide, Inches(0.5), top, cbw, bullet_h, T["accent_color"])
        add_textbox(
            slide,
            {"left": Inches(0.5) + cbw + Inches(0.15), "top": top, "width": bullet_width, "height": bullet_h},
            bullet, T["font_body"], T["font_size_body"], T["text_color"],
            auto_size=True,
        )
    if imagen:
        _insert_image(slide, imagen)


def build_destacado(slide, data: dict, tpl, imagen=None) -> None:
    """Destacado corporativo_neutro: header navy + caja header_color con texto blanco."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["destacado"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["header_height"], T["header_color"])
    add_rect(slide, Inches(0), L["header_height"], _W, L["acento_height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], "FFFFFF", bold=True)
    panel_width = Inches(7.0) if imagen else Inches(12.5)
    box = add_rect(slide, Inches(0.4), Inches(1.3), panel_width, Inches(5.8), T["header_color"])
    set_shape_text(box, str(data.get("contenido", "")), T["font_body"], T["font_size_body"], "FFFFFF")
    if imagen:
        _insert_image(slide, imagen)


def build_cierre(slide, data: dict, tpl) -> None:
    """Cierre corporativo_neutro: panel derecho navy con título blanco, fondo gris claro."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["cierre"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, L["panel_dcho_x"], Inches(0), L["panel_dcho_width"], _H, T["header_color"])
    pb = L["panel_borde"]
    add_rect(slide, pb["left"], pb["top"], pb["width"], pb["height"], T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], "FFFFFF", bold=True)
    contenido = data.get("contenido")
    if contenido and str(contenido).strip():
        add_textbox(
            slide,
            {"left": Inches(0.5), "top": Inches(3.0), "width": Inches(7.5), "height": Inches(3.5)},
            str(contenido), T["font_body"], T["font_size_body"], T["text_color"],
        )


def _insert_image(slide, imagen) -> None:
    """Inserta imagen en zona izquierda inferior. Falla silenciosamente."""
    try:
        img_bytes = imagen if isinstance(imagen, bytes) else imagen[1]
        slide.shapes.add_picture(
            io.BytesIO(img_bytes),
            left=int(Inches(7.8)), top=int(Inches(1.3)),
            width=int(Inches(5.0)), height=int(Inches(5.8)),
        )
    except Exception:
        pass
