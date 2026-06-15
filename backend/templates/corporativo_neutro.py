"""Template corporativo_neutro — solo tokens de color/fuente.

La geometría es compartida (services/pptx_geometry.LAYOUTS); este módulo aporta
únicamente la paleta. Tema CLARO/neutro: fondo gris claro, cards claras, texto oscuro.
"""
TEMPLATE = {
    "template_name": "corporativo_neutro",
    # Paleta — mismo vocabulario de tokens que el resto de templates.
    "background": "F0F4F8",
    "accent": "1ABC9C",
    "surface": "FFFFFF",             # panel destacado claro (texto oscuro encima)
    "card_primary": "FFFFFF",        # card clara (estado destacado/completado)
    "card_secondary": "E4ECF2",      # card clara alterna (contraste con la primary)
    "text": "1A252F",
    "text_secondary": "2C3E50",
    "on_accent": "FFFFFF",           # texto sobre accent (ej. número de step)
    "state_in_progress": "9A4A06",   # ámbar oscuro: >=4.5:1 sobre cards claras
    "state_done": "0D6E63",          # teal oscuro (hue accent): >=4.5:1 sobre cards claras
    # Tipografía
    "font_title": "Cambria",
    "font_body": "Calibri",
    "font_size_title_portada": 36,
    "font_size_title_slide": 26,
    "font_size_body": 15,
}
