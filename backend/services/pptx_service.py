import io
from typing import Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.util import Cm, Pt

from templates import corporativo_neutro, ejecutivo_oscuro, profesional_claro
from utils.errors import AppError, ErrorCode
from utils.pptx_helpers import add_textbox, set_slide_background

TEMPLATES = {
    "ejecutivo_oscuro": ejecutivo_oscuro,
    "profesional_claro": profesional_claro,
    "corporativo_neutro": corporativo_neutro,
}


def _build_portada(slide, data: dict, tpl) -> None:
    """
    Construye slide de portada: fondo sólido, título grande en accent_color,
    subtítulo debajo en secondary_text.

    Args:
        slide: objeto slide de python-pptx.
        data: dict con 'titulo' (str) y 'contenido' (str).
        tpl: módulo de template con atributos TEMPLATE y LAYOUTS.
    """
    t = tpl.TEMPLATE
    lay = tpl.LAYOUTS["portada"]
    set_slide_background(slide, t["background_color"])
    add_textbox(slide, lay["title"], data["titulo"], t["font_title"], t["font_size_title_portada"], t["accent_color"], bold=True)
    add_textbox(slide, lay["subtitle"], str(data["contenido"]), t["font_body"], t["font_size_body"], t["secondary_text"])


def _build_contenido(slide, data: dict, tpl) -> None:
    """
    Construye slide de contenido: fondo, título en accent_color, bullets en text_color.
    Cada bullet lleva prefijo '•'. Se renderizan máximo 5.

    Args:
        slide: objeto slide de python-pptx.
        data: dict con 'titulo' (str) y 'contenido' (list[str]).
        tpl: módulo de template con atributos TEMPLATE y LAYOUTS.
    """
    t = tpl.TEMPLATE
    lay = tpl.LAYOUTS["contenido"]
    set_slide_background(slide, t["background_color"])
    add_textbox(slide, lay["title"], data["titulo"], t["font_title"], t["font_size_title_slide"], t["accent_color"], bold=True)
    bullets = data["contenido"] if isinstance(data["contenido"], list) else [str(data["contenido"])]
    bullet_text = "\n".join(f"• {b}" for b in bullets[:5])
    add_textbox(slide, lay["body"], bullet_text, t["font_body"], t["font_size_body"], t["text_color"])


def _build_destacado(slide, data: dict, tpl) -> None:
    """
    Construye slide destacado: fondo, título en accent_color, texto central en
    rectángulo relleno (fondo accent_color, texto background_color).

    Args:
        slide: objeto slide de python-pptx.
        data: dict con 'titulo' (str) y 'contenido' (str).
        tpl: módulo de template con atributos TEMPLATE y LAYOUTS.
    """
    t = tpl.TEMPLATE
    lay = tpl.LAYOUTS["destacado"]
    set_slide_background(slide, t["background_color"])
    add_textbox(slide, lay["title"], data["titulo"], t["font_title"], t["font_size_title_slide"], t["accent_color"], bold=True)
    box = lay["box"]
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, box["left"], box["top"], box["width"], box["height"])
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(t["accent_color"])
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = str(data["contenido"])
    run = tf.paragraphs[0].runs[0]
    run.font.name = t["font_body"]
    run.font.size = Pt(t["font_size_body"])
    run.font.color.rgb = RGBColor.from_string(t["background_color"])


def _build_cierre(slide, data: dict, tpl) -> None:
    """
    Construye slide de cierre: fondo, texto centrado en accent_color,
    línea horizontal decorativa debajo en secondary_text.

    Args:
        slide: objeto slide de python-pptx.
        data: dict con 'titulo' (str) y 'contenido' (str).
        tpl: módulo de template con atributos TEMPLATE y LAYOUTS.
    """
    t = tpl.TEMPLATE
    lay = tpl.LAYOUTS["cierre"]
    set_slide_background(slide, t["background_color"])
    add_textbox(slide, lay["text"], data["titulo"], t["font_title"], t["font_size_title_portada"], t["accent_color"], bold=True)
    ln = lay["line"]
    line_shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, ln["left"], ln["top"], ln["width"], ln["height"])
    line_shape.fill.solid()
    line_shape.fill.fore_color.rgb = RGBColor.from_string(t["secondary_text"])
    line_shape.line.fill.background()


def _insert_logo_pptx(slide, logo_bytes: bytes) -> None:
    """Inserta logo pequeño en la esquina superior izquierda del slide. Falla silenciosamente."""
    try:
        slide.shapes.add_picture(io.BytesIO(logo_bytes), left=Cm(0.5), top=Cm(0.3), height=Cm(2.1))
    except Exception:
        pass


def generate_pptx(outline: dict, template_name: str, logo_bytes: Optional[bytes] = None) -> bytes:
    """
    Genera un archivo .pptx a partir de un outline dict y el nombre de un template.

    Args:
        outline: dict con 'titulo_presentacion' (str) y 'slides' (list[dict]).
                 Cada slide tiene 'tipo', 'titulo' y 'contenido'.
        template_name: nombre del template. Valores: 'ejecutivo_oscuro' |
                       'profesional_claro' | 'corporativo_neutro'.

    Returns:
        Bytes del archivo .pptx generado, listos para enviar como descarga.

    Raises:
        AppError: code TEMPLATE_NOT_FOUND (400) si template_name no existe en TEMPLATES.
        AppError: code PPTX_BUILD_ERROR (503) si la generación del archivo falla.
    """
    if template_name not in TEMPLATES:
        raise AppError("Template no encontrado", ErrorCode.TEMPLATE_NOT_FOUND, 400)
    tpl = TEMPLATES[template_name]
    _builders = {
        "portada": _build_portada,
        "contenido": _build_contenido,
        "destacado": _build_destacado,
        "cierre": _build_cierre,
    }
    try:
        prs = Presentation()
        blank_layout = prs.slide_layouts[6]
        for idx, slide_data in enumerate(outline["slides"]):
            slide = prs.slides.add_slide(blank_layout)
            builder = _builders.get(slide_data["tipo"])
            if builder:
                builder(slide, slide_data, tpl)
            if idx == 0 and logo_bytes:
                _insert_logo_pptx(slide, logo_bytes)
        buffer = io.BytesIO()
        prs.save(buffer)
        return buffer.getvalue()
    except AppError:
        raise
    except Exception as exc:
        raise AppError("Error generando PPTX", ErrorCode.PPTX_BUILD_ERROR, 503) from exc
