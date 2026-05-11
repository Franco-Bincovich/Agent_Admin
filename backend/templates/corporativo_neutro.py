from pptx.util import Inches

TEMPLATE = {
    "template_name": "corporativo_neutro",
    "background_color": "F0F4F8",
    "header_color": "1B4F72",
    "accent_color": "1ABC9C",
    "text_color": "1A252F",
    "secondary_text": "2C3E50",
    "card_color": "FFFFFF",
    "font_title": "Cambria",
    "font_body": "Calibri",
    "font_size_title_portada": 36,
    "font_size_title_slide": 26,
    "font_size_body": 15,
}

LAYOUTS = {
    "portada": {
        "panel_dcho_x": Inches(7.5),
        "panel_dcho_width": Inches(5.83),
        "panel_borde": {
            "left": Inches(7.4), "top": Inches(0),
            "width": Inches(0.1), "height": Inches(7.5),
        },
        "titulo": {
            "left": Inches(7.8), "top": Inches(1.8),
            "width": Inches(5.0), "height": Inches(3.5),
        },
        "subtitulo": {
            "left": Inches(7.8), "top": Inches(5.5),
            "width": Inches(5.0), "height": Inches(0.6),
        },
        "descripcion": {
            "left": Inches(0.5), "top": Inches(2.8),
            "width": Inches(6.5), "height": Inches(2.0),
        },
        "empresa_label": {
            "left": Inches(0.5), "top": Inches(1.8),
            "width": Inches(4.0), "height": Inches(0.5),
        },
    },
    "contenido": {
        "header_height": Inches(1.05),
        "acento_height": Inches(0.07),
        "titulo": {
            "left": Inches(0.5), "top": Inches(0.18),
            "width": Inches(12.0), "height": Inches(0.7),
        },
        "bullets_start_y": Inches(1.5),
        "bullet_height": Inches(1.0),
        "card_height": Inches(0.8),
        "card_borde_width": Inches(0.07),
    },
    "destacado": {
        "header_height": Inches(1.05),
        "acento_height": Inches(0.07),
        "titulo": {
            "left": Inches(0.5), "top": Inches(0.18),
            "width": Inches(12.0), "height": Inches(0.7),
        },
        "box": {
            "left": Inches(0.5), "top": Inches(1.5),
            "width": Inches(12.3), "height": Inches(4.5),
        },
    },
    "cierre": {
        "panel_dcho_x": Inches(7.5),
        "panel_dcho_width": Inches(5.83),
        "panel_borde": {
            "left": Inches(7.4), "top": Inches(0),
            "width": Inches(0.1), "height": Inches(7.5),
        },
        "titulo": {
            "left": Inches(7.8), "top": Inches(2.5),
            "width": Inches(5.0), "height": Inches(2.5),
        },
    },
}
