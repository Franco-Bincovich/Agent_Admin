from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.util import Pt


def set_slide_background(slide, hex_color: str) -> None:
    """Sets a solid background color on a slide."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(hex_color)


def add_textbox(
    slide, pos: dict, text: str, font: str, size: int, color: str, bold: bool = False
) -> None:
    """Adds a formatted text box to the slide at the given position dict."""
    txb = slide.shapes.add_textbox(pos["left"], pos["top"], pos["width"], pos["height"])
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    if p.runs:
        run = p.runs[0]
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string(color)
        run.font.bold = bold


def add_rect(slide, left, top, width, height, color: str):
    """Adds a solid filled rectangle with no border. Returns the shape."""
    sh = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(color)
    sh.line.fill.background()
    return sh


def set_shape_text(sh, text: str, font: str, size: int, color: str, bold: bool = False) -> None:
    """Writes formatted text into an existing shape's text frame."""
    tf = sh.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    if p.runs:
        run = p.runs[0]
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string(color)
        run.font.bold = bold
