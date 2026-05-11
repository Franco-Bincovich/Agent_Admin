from __future__ import annotations

import services.pptx_builder_claro as _claro
import services.pptx_builder_neutro as _neutro
import services.pptx_builder_oscuro as _oscuro

_BUILDERS = {
    "profesional_claro": _claro,
    "ejecutivo_oscuro": _oscuro,
    "corporativo_neutro": _neutro,
}


def _get_module(tpl):
    """Devuelve el módulo builder correspondiente al template_name del tpl."""
    return _BUILDERS[tpl.TEMPLATE["template_name"]]


def _build_portada(slide, data: dict, tpl) -> None:
    """Construye slide de portada delegando al módulo del template activo."""
    _get_module(tpl).build_portada(slide, data, tpl)


def _build_contenido(slide, data: dict, tpl, imagen=None) -> None:
    """Construye slide de contenido delegando al módulo del template activo."""
    _get_module(tpl).build_contenido(slide, data, tpl, imagen)


def _build_destacado(slide, data: dict, tpl, imagen=None) -> None:
    """Construye slide destacado delegando al módulo del template activo."""
    _get_module(tpl).build_destacado(slide, data, tpl, imagen)


def _build_cierre(slide, data: dict, tpl) -> None:
    """Construye slide de cierre delegando al módulo del template activo."""
    _get_module(tpl).build_cierre(slide, data, tpl)
