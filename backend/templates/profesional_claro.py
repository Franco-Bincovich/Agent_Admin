"""Template profesional_claro — solo tokens de color/fuente.

La geometría es compartida (services/pptx_geometry.LAYOUTS); este módulo aporta
únicamente la paleta. Tema CLARO: superficies/cards claras, texto oscuro.
"""
TEMPLATE = {
    "template_name": "profesional_claro",
    # Paleta — mismo vocabulario de tokens que el resto de templates.
    "background": "FFFFFF",
    "accent": "4A9FD4",
    "surface": "EAF1F8",             # panel destacado claro (texto oscuro encima)
    "card_primary": "DCE8F4",        # card clara (estado destacado/completado)
    "card_secondary": "EEF4FA",      # card clara alterna
    "text": "222222",
    "text_secondary": "555555",
    "on_accent": "FFFFFF",           # texto sobre accent (ej. número de step)
    "state_in_progress": "9A4A06",   # ámbar oscuro: >=4.5:1 sobre cards claras
    "state_done": "21618C",          # azul oscuro (hue accent): >=4.5:1 sobre cards claras
    # Tipografía
    "font_title": "Trebuchet MS",
    "font_body": "Calibri",
    "font_size_title_portada": 34,
    "font_size_title_slide": 26,
    "font_size_body": 16,
}
