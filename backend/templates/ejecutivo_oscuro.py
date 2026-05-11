from pptx.util import Inches

TEMPLATE = {
    "template_name": "ejecutivo_oscuro",
    "background_color": "0A1628",
    "accent_color": "4FC3F7",
    "panel_color": "0E2A4A",
    "text_color": "FFFFFF",
    "secondary_text": "E8F4FD",
    "font_title": "Calibri",
    "font_body": "Calibri",
    "font_size_title_portada": 48,
    "font_size_title_slide": 28,
    "font_size_body": 16,
}

LAYOUTS = {
    "portada": {
        "banda_top_height": Inches(0.08),
        "banda_bottom_height": Inches(0.08),
        "panel_deco": {
            "left": Inches(9.5), "top": Inches(1.5),
            "width": Inches(3.5), "height": Inches(4.5),
        },
        "panel_borde": {
            "left": Inches(9.4), "top": Inches(1.5),
            "width": Inches(0.08), "height": Inches(4.5),
        },
        "titulo": {
            "left": Inches(0.6), "top": Inches(1.8),
            "width": Inches(8.5), "height": Inches(3.5),
        },
        "subtitulo": {
            "left": Inches(0.6), "top": Inches(5.5),
            "width": Inches(8.5), "height": Inches(0.6),
        },
        "linea_sep": {
            "left": Inches(0.6), "top": Inches(5.3),
            "width": Inches(3.5), "height": Inches(0.04),
        },
    },
    "contenido": {
        "banda_top_height": Inches(0.08),
        "titulo": {
            "left": Inches(0.6), "top": Inches(0.3),
            "width": Inches(12.0), "height": Inches(0.8),
        },
        "linea_titulo": {
            "left": Inches(0.6), "top": Inches(1.1),
            "width": Inches(4.0), "height": Inches(0.04),
        },
        "bullets_start_y": Inches(1.4),
        "bullet_height": Inches(1.0),
        "bullet_dot_size": Inches(0.12),
    },
    "destacado": {
        "banda_top_height": Inches(0.08),
        "titulo": {
            "left": Inches(0.6), "top": Inches(0.3),
            "width": Inches(12.0), "height": Inches(0.8),
        },
        "linea_titulo": {
            "left": Inches(0.6), "top": Inches(1.1),
            "width": Inches(4.0), "height": Inches(0.04),
        },
        "box": {
            "left": Inches(0.6), "top": Inches(1.5),
            "width": Inches(12.0), "height": Inches(4.5),
        },
    },
    "cierre": {
        "titulo": {
            "left": Inches(0.6), "top": Inches(2.2),
            "width": Inches(12.0), "height": Inches(3.0),
        },
        "linea": {
            "left": Inches(0.6), "top": Inches(5.5),
            "width": Inches(4.0), "height": Inches(0.04),
        },
    },
}
