from pptx.util import Inches

TEMPLATE = {
    "template_name": "profesional_claro",
    "background_color": "FFFFFF",
    "header_color": "1E3A5F",
    "accent_color": "4A9FD4",
    "text_color": "222222",
    "secondary_text": "555555",
    "font_title": "Trebuchet MS",
    "font_body": "Calibri",
    "font_size_title_portada": 34,
    "font_size_title_slide": 26,
    "font_size_body": 16,
}

LAYOUTS = {
    "portada": {
        "panel_izq_width": Inches(4.2),
        "titulo": {
            "left": Inches(0.4), "top": Inches(2.2),
            "width": Inches(3.5), "height": Inches(3.0),
        },
        "subtitulo": {
            "left": Inches(0.4), "top": Inches(5.4),
            "width": Inches(3.5), "height": Inches(0.6),
        },
        "descripcion": {
            "left": Inches(4.6), "top": Inches(3.0),
            "width": Inches(8.3), "height": Inches(1.8),
        },
        "linea_acento": {
            "left": Inches(4.6), "top": Inches(2.7),
            "width": Inches(1.2), "height": Inches(0.06),
        },
    },
    "contenido": {
        "header_height": Inches(1.1),
        "titulo": {
            "left": Inches(0.4), "top": Inches(0.18),
            "width": Inches(12.0), "height": Inches(0.75),
        },
        "bullets_start_y": Inches(1.5),
        "bullet_height": Inches(1.0),
        "bullet_box_size": Inches(0.5),
        "bullet_text_x": Inches(1.1),
    },
    "destacado": {
        "header_height": Inches(1.1),
        "titulo": {
            "left": Inches(0.4), "top": Inches(0.18),
            "width": Inches(12.0), "height": Inches(0.75),
        },
        "box": {
            "left": Inches(0.6), "top": Inches(1.5),
            "width": Inches(12.0), "height": Inches(4.5),
        },
    },
    "cierre": {
        "panel_izq_width": Inches(4.2),
        "titulo": {
            "left": Inches(0.4), "top": Inches(2.5),
            "width": Inches(3.5), "height": Inches(2.5),
        },
    },
}
