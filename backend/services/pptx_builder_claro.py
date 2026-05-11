from __future__ import annotations

import io

from pptx.util import Inches

from utils.pptx_helpers import add_rect, add_textbox, set_shape_text, set_slide_background

_W = Inches(13.33)
_H = Inches(7.5)


def build_portada(slide, data: dict, tpl) -> None:
    """Portada profesional_claro: banda izquierda navy, título + subtítulo en banda, descripción a la derecha."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["portada"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), L["panel_izq_width"], _H, T["header_color"])
    add_rect(slide, L["panel_izq_width"], Inches(0), Inches(0.06), _H, T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], "FFFFFF", bold=True)
    add_textbox(slide, L["subtitulo"], str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["accent_color"])
    la = L["linea_acento"]
    add_rect(slide, la["left"], la["top"], la["width"], la["height"], T["accent_color"])
    add_textbox(slide, L["descripcion"], str(data.get("contenido", "")), T["font_body"], T["font_size_body"], T["secondary_text"])


def build_contenido(slide, data: dict, tpl, imagen=None) -> None:
    """Contenido profesional_claro: header navy + línea accent + bullets numerados con cajita navy."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["contenido"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["header_height"], T["header_color"])
    add_rect(slide, Inches(0), L["header_height"], _W, Inches(0.06), T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], "FFFFFF", bold=True)
    bullets = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    bs = L["bullet_box_size"]
    for i, bullet in enumerate(bullets[:5]):
        top = L["bullets_start_y"] + i * L["bullet_height"]
        num_box = add_rect(slide, Inches(0.5), top, bs, bs, T["header_color"])
        set_shape_text(num_box, str(i + 1), T["font_body"], T["font_size_body"] - 2, "FFFFFF", bold=True)
        add_textbox(
            slide,
            {"left": L["bullet_text_x"], "top": top, "width": Inches(11.5), "height": bs},
            bullet, T["font_body"], T["font_size_body"], T["text_color"],
        )
    if imagen:
        _insert_image(slide, imagen)


def build_destacado(slide, data: dict, tpl, imagen=None) -> None:
    """Destacado profesional_claro: header navy + caja header_color con texto blanco."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["destacado"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), _W, L["header_height"], T["header_color"])
    add_rect(slide, Inches(0), L["header_height"], _W, Inches(0.06), T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_slide"], "FFFFFF", bold=True)
    box = add_rect(slide, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.8), T["header_color"])
    set_shape_text(box, str(data.get("contenido", "")), T["font_body"], T["font_size_body"], "FFFFFF")
    if imagen:
        _insert_image(slide, imagen)


def build_cierre(slide, data: dict, tpl) -> None:
    """Cierre profesional_claro: banda izquierda navy + título centrado en blanco."""
    T, L = tpl.TEMPLATE, tpl.LAYOUTS["cierre"]
    set_slide_background(slide, T["background_color"])
    add_rect(slide, Inches(0), Inches(0), L["panel_izq_width"], _H, T["header_color"])
    add_rect(slide, L["panel_izq_width"], Inches(0), Inches(0.06), _H, T["accent_color"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], T["font_size_title_portada"], "FFFFFF", bold=True)


def _insert_image(slide, imagen) -> None:
    """Inserta imagen a la derecha del área de texto. Falla silenciosamente."""
    try:
        _, img_bytes = imagen
        slide.shapes.add_picture(
            io.BytesIO(img_bytes),
            left=int(Inches(8.0)), top=int(Inches(2.5)), width=int(Inches(4.8)),
        )
    except Exception:
        pass
