"""Template ejecutivo_oscuro — solo tokens de color/fuente.

La geometría es compartida (services/pptx_geometry.LAYOUTS); este módulo aporta
únicamente la paleta. Tema oscuro.
"""
TEMPLATE = {
    "template_name": "ejecutivo_oscuro",
    # Paleta — tokens semánticos normalizados (compartidos por todos los templates).
    "background": "060D1F",
    "accent": "4FC3F7",
    "surface": "0D2137",
    "card_primary": "1A3A5C",
    "card_secondary": "0D1F35",
    "text": "FFFFFF",
    "text_secondary": "E8F4FD",
    "on_accent": "060D1F",           # texto sobre accent (ej. número de step)
    "state_in_progress": "F59E0B",
    "state_done": "4FC3F7",
    # Tipografía
    "font_title": "Calibri",
    "font_body": "Calibri",
    "font_size_title_portada": 48,
    "font_size_title_slide": 28,
    "font_size_body": 16,
}
