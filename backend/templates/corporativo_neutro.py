from pptx.util import Inches

TEMPLATE = {
    "background_color": "1E1E2E",
    "text_color": "E2E8F0",
    "accent_color": "7C3AED",
    "secondary_text": "94A3B8",
    "font_title": "Calibri",
    "font_body": "Calibri",
    "font_size_title_portada": 36,
    "font_size_title_slide": 28,
    "font_size_body": 18,
    "font_size_label": 13,
}

LAYOUTS = {
    "portada": {
        "title": {
            "left": Inches(1),
            "top": Inches(2),
            "width": Inches(8),
            "height": Inches(2),
        },
        "subtitle": {
            "left": Inches(1),
            "top": Inches(4.3),
            "width": Inches(8),
            "height": Inches(1),
        },
    },
    "contenido": {
        "title": {
            "left": Inches(0.5),
            "top": Inches(0.3),
            "width": Inches(9),
            "height": Inches(0.9),
        },
        "body": {
            "left": Inches(0.5),
            "top": Inches(1.4),
            "width": Inches(9),
            "height": Inches(5.8),
        },
    },
    "destacado": {
        "title": {
            "left": Inches(0.5),
            "top": Inches(0.3),
            "width": Inches(9),
            "height": Inches(0.9),
        },
        "box": {
            "left": Inches(1),
            "top": Inches(1.8),
            "width": Inches(8),
            "height": Inches(3.5),
        },
    },
    "cierre": {
        "text": {
            "left": Inches(1),
            "top": Inches(2.3),
            "width": Inches(8),
            "height": Inches(2),
        },
        "line": {
            "left": Inches(1),
            "top": Inches(5),
            "width": Inches(8),
            "height": Inches(0.05),
        },
    },
}
