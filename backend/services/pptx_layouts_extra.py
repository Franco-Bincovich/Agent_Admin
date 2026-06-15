"""Motor de layouts PPTX — layouts nuevos: cards_3, timeline, split_2col, steps.

Implementación única compartida por todos los templates. La geometría viene de
pptx_geometry.LAYOUTS (compartida); el color/fuente, solo de tpl.TEMPLATE (tokens).
"""
from __future__ import annotations

from pptx.util import Inches

from services.pptx_geometry import _H, _W, LAYOUTS
from utils.pptx_helpers import (
    _rrect,
    _titulo_font_size,
    add_rect,
    add_textbox,
    set_slide_background,
)


def build_cards_3(slide, data: dict, tpl) -> None:
    """Cards_3: 3 cards card_primary/secondary de ancho completo con borde accent superior."""
    T, L = tpl.TEMPLATE, LAYOUTS["cards_3"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    items = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    cw, ch, ct = L["card_width"], L["card_height"], L["card_top"]
    sx, gap = L["card_start_x"], L["card_gap"]
    _c_pri = T["card_primary"]
    _c_sec = T["card_secondary"]
    card_colors = [_c_pri, _c_sec, _c_sec]
    for i in range(3):
        x = sx + i * (cw + gap)
        _rrect(slide, x, ct, cw, ch, card_colors[i])
        item = items[i] if i < len(items) else {}
        if isinstance(item, dict):
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.2), "width": cw - Inches(0.4), "height": Inches(0.65)},
                str(item.get("num", "")), T["font_title"], 26, T["accent"], bold=True,
            )
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.95), "width": cw - Inches(0.4), "height": Inches(0.75)},
                str(item.get("titulo", "")), T["font_body"], T["font_size_body"] + 2, T["text"], bold=True,
            )
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(1.85), "width": cw - Inches(0.4), "height": ch - Inches(2.05)},
                str(item.get("descripcion", "")), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
        else:
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.15), "width": cw - Inches(0.4), "height": ch - Inches(0.25)},
                str(item), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )


def build_timeline(slide, data: dict, tpl) -> None:
    """Timeline: cards verticales con fecha 20pt, descripción e indicador de estado."""
    T, L = tpl.TEMPLATE, LAYOUTS["timeline"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    items = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    cw, ch, ct = L["card_width"], L["card_height"], L["card_top"]
    sx, gap = L["card_start_x"], L["card_gap"]
    total_w = 3 * cw + 2 * gap
    _c_pri = T["card_primary"]
    _c_sec = T["card_secondary"]
    for i in range(3):
        x = sx + i * (cw + gap)
        item = items[i] if i < len(items) else {}
        estado = item.get("estado", "") if isinstance(item, dict) else ""
        card_bg = _c_pri if estado == "completado" else _c_sec
        _rrect(slide, x, ct, cw, ch, card_bg)
        if isinstance(item, dict):
            fecha = str(item.get("fecha", ""))
            descripcion = str(item.get("descripcion", ""))
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.15), "width": cw - Inches(0.4), "height": Inches(0.5)},
                fecha, T["font_body"], 20, T["accent"], bold=True,
            )
            desc_h = ch - Inches(1.3) if estado in ("completado", "en_curso") else ch - Inches(0.85)
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.7), "width": cw - Inches(0.4), "height": desc_h},
                descripcion, T["font_body"], 13, T["text_secondary"], auto_size=True,
            )
            if estado == "completado":
                add_textbox(
                    slide,
                    {"left": x + Inches(0.2), "top": ct + ch - Inches(0.5), "width": cw - Inches(0.4), "height": Inches(0.4)},
                    "✓ Completado", T["font_body"], 11, T["state_done"], bold=True,
                )
            elif estado == "en_curso":
                add_textbox(
                    slide,
                    {"left": x + Inches(0.2), "top": ct + ch - Inches(0.5), "width": cw - Inches(0.4), "height": Inches(0.4)},
                    "→ En curso", T["font_body"], 11, T["state_in_progress"], bold=True,
                )
        else:
            add_textbox(
                slide,
                {"left": x + Inches(0.18), "top": ct + Inches(0.12), "width": cw - Inches(0.36), "height": ch - Inches(0.22)},
                str(item), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
    footer = data.get("footer", "")
    if footer:
        add_textbox(
            slide,
            {"left": sx, "top": L["footer_top"], "width": total_w, "height": Inches(0.5)},
            str(footer), T["font_body"], T["font_size_body"] - 2, T["text_secondary"],
        )


def build_split_2col(slide, data: dict, tpl) -> None:
    """Split_2col: 2 columnas iguales card_primary/secondary de ancho completo con borde accent."""
    T, L = tpl.TEMPLATE, LAYOUTS["split_2col"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    contenido = data.get("contenido", "")
    if isinstance(contenido, list) and len(contenido) >= 2:
        col_items = contenido[:2]
    elif isinstance(contenido, dict):
        col_items = [contenido.get("izquierda", ""), contenido.get("derecha", "")]
    else:
        col_items = [str(contenido), ""]
    cw, ch, ct = L["card_width"], L["card_height"], L["card_top"]
    lx, rx = L["card_left_x"], L["card_right_x"]
    _c_pri = T["card_primary"]
    _c_sec = T["card_secondary"]
    for x, item, card_bg in zip((lx, rx), col_items, (_c_pri, _c_sec)):
        _rrect(slide, x, ct, cw, ch, card_bg)
        if isinstance(item, dict):
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.15), "width": cw - Inches(0.4), "height": Inches(0.75)},
                str(item.get("titulo", "")), T["font_body"], T["font_size_body"] + 2, T["text"], bold=True,
            )
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(1.0), "width": cw - Inches(0.4), "height": ch - Inches(1.15)},
                str(item.get("descripcion", "")), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
        else:
            add_textbox(
                slide,
                {"left": x + Inches(0.2), "top": ct + Inches(0.15), "width": cw - Inches(0.4), "height": ch - Inches(0.25)},
                str(item), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
    footer = data.get("footer", "")
    if footer:
        add_textbox(
            slide,
            {"left": lx, "top": L["footer_top"], "width": cw * 2 + Inches(0.5), "height": Inches(0.5)},
            str(footer), T["font_body"], T["font_size_body"] - 2, T["text_secondary"],
        )


def build_steps(slide, data: dict, tpl) -> None:
    """Steps: pasos numerados verticales, step_height hasta 1.8" para llenar el slide."""
    T, L = tpl.TEMPLATE, LAYOUTS["steps"]
    set_slide_background(slide, T["background"])
    add_rect(slide, Inches(0), Inches(0), _W, L["banda_top_height"], T["accent"])
    add_textbox(slide, L["titulo"], data["titulo"], T["font_title"], _titulo_font_size(data["titulo"], T["font_size_title_slide"]), T["text"], bold=True)
    lt = L["linea_titulo"]
    add_rect(slide, lt["left"], lt["top"], lt["width"], lt["height"], T["accent"])
    steps = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    n = len(steps[:5])
    available_h = _H - L["steps_start_y"] - Inches(0.3)
    # AJUSTE 5: máximo 1.8" (era 1.4")
    step_h = min(Inches(1.8), max(Inches(0.65), available_h / n))
    circle_d = Inches(0.38)
    for i, step in enumerate(steps[:5]):
        top = L["steps_start_y"] + i * step_h
        cy = top + (step_h - circle_d) / 2
        _rrect(slide, Inches(0.5), cy, circle_d, circle_d, T["accent"], radius=0.5)
        add_textbox(
            slide,
            {"left": Inches(0.5), "top": cy, "width": circle_d, "height": circle_d},
            str(i + 1), T["font_body"], 13, T["on_accent"], bold=True,
        )
        _rrect(slide, Inches(1.1), top + Inches(0.06), Inches(11.7), step_h - Inches(0.12), T["card_secondary"])
        if isinstance(step, dict):
            add_textbox(
                slide,
                {"left": Inches(1.35), "top": top + Inches(0.08), "width": Inches(11.3), "height": Inches(0.55)},
                str(step.get("titulo", "")), T["font_body"], T["font_size_body"], T["text"], bold=True,
            )
            add_textbox(
                slide,
                {"left": Inches(1.35), "top": top + Inches(0.65), "width": Inches(11.3), "height": step_h - Inches(0.72)},
                str(step.get("descripcion", "")), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
        else:
            add_textbox(
                slide,
                {"left": Inches(1.35), "top": top + Inches(0.06), "width": Inches(11.3), "height": step_h - Inches(0.12)},
                str(step), T["font_body"], T["font_size_body"], T["text_secondary"], auto_size=True,
            )
