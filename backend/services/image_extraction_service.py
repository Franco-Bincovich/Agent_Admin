from __future__ import annotations

import io
import os
import unicodedata
import zipfile
from pathlib import Path

import fitz

_MIN_IMAGE_BYTES = 5 * 1024
_MIN_TEXT_PER_PAGE = 100  # chars avg — below this triggers EMF extraction


def extract_images_from_file(filename: str, file_bytes: bytes) -> list[bytes]:
    """
    Extracts embedded images from a file, detecting type by extension.

    Supports:
    - .pdf  → PyMuPDF: extracts images page by page via get_images().
    - .docx → rasterizes full pages with PyMuPDF (captures EMF/WMF)
              plus inline images from word/media/.
    - .xlsx → extracts images from xl/media/; returns [] without error.

    Returns [] silently on any failure to avoid blocking the main pipeline.
    """
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".pdf":
            return _extract_images_from_pdf(file_bytes)
        if ext == ".docx":
            return _extract_images_from_docx(file_bytes)
        if ext == ".xlsx":
            return _extract_images_from_xlsx(file_bytes)
        return []
    except Exception:
        return []


def _extract_images_from_pdf(file_bytes: bytes) -> list[bytes]:
    """Extracts images from each page of a PDF using PyMuPDF."""
    images: list[bytes] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        for img_index in page.get_images():
            xref = img_index[0]
            base_image = doc.extract_image(xref)
            img = base_image["image"]
            if len(img) >= _MIN_IMAGE_BYTES:
                images.append(img)
    doc.close()
    return images


def _convert_emf_to_png(emf_bytes: bytes) -> bytes | None:
    """
    Converts EMF/WMF bytes to PNG via a three-step fallback chain.

    1. fitz native EMF rendering (filetype='emf').
    2. fitz SVG path — MuPDF sometimes accepts EMF as SVG.
    3. PIL if available as a transitive dependency.
    4. A fitz-generated placeholder page with explanatory text.

    Returns PNG bytes, or None if every method fails.
    """
    for filetype in ("emf", "svg"):
        try:
            doc = fitz.open(stream=emf_bytes, filetype=filetype)
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
            png = pix.tobytes("png")
            doc.close()
            return png
        except Exception:
            pass

    try:
        from PIL import Image  # type: ignore[import]
        buf = io.BytesIO()
        Image.open(io.BytesIO(emf_bytes)).save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        pass

    try:
        doc = fitz.open()
        page = doc.new_page(width=800, height=400)
        page.insert_text((20, 200), "Contenido visual no extraíble", fontsize=16)
        png = page.get_pixmap().tobytes("png")
        doc.close()
        return png
    except Exception:
        return None


def _extract_emf_from_docx(file_bytes: bytes) -> list[bytes]:
    """
    Extracts EMF/WMF files from the DOCX ZIP and converts each to PNG.

    Returns a list of PNG bytes for every image successfully converted.
    Silently skips images that fail all conversion attempts.
    """
    results: list[bytes] = []
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            for name in zf.namelist():
                if name.startswith("word/media/") and Path(name).suffix.lower() in (".emf", ".wmf"):
                    png = _convert_emf_to_png(zf.read(name))
                    if png:
                        results.append(png)
    except Exception:
        pass
    return results


def _extract_pages_from_docx_as_images(file_bytes: bytes) -> list[bytes]:
    """
    Rasterizes DOCX pages to PNG at 150 DPI.

    When the average text per page is below _MIN_TEXT_PER_PAGE chars, content
    is likely stored as EMF/WMF images (not selectable text). In that case the
    EMF files are also extracted from word/media/ and converted to PNG, then
    appended after the rasterized pages so Claude can read their visual content.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="docx")
        images: list[bytes] = []
        total_text = 0
        for page in doc:
            total_text += len(page.get_text().strip())
            pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
            images.append(pix.tobytes("png"))
        doc.close()
        if images and (total_text / len(images)) < _MIN_TEXT_PER_PAGE:
            return images + _extract_emf_from_docx(file_bytes)
        return images
    except Exception:
        return []


def _extract_images_from_docx(file_bytes: bytes) -> list[bytes]:
    """
    Extracts inline images (PNG/JPG/GIF) from a DOCX for use as slide illustrations.

    Returns only the images embedded in word/media/ — rasterized document pages are
    intentionally excluded. Pages travel via extract_docx_pages_as_images() →
    imagenes_contenido and are used solely as vision input for Claude to read tables.
    Mixing them into this pool caused raw document scans to appear inside slides.
    """
    _SUPPORTED = {".png", ".jpg", ".jpeg", ".gif"}
    inline: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if not name.startswith("word/media/"):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in _SUPPORTED:
                continue
            img = zf.read(name)
            if len(img) >= _MIN_IMAGE_BYTES:
                inline.append(img)
    return inline


def _extract_images_from_xlsx(file_bytes: bytes) -> list[bytes]:
    """Extracts images from xl/media/ inside the XLSX ZIP."""
    _IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    images: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if name.startswith("xl/media/") and Path(name).suffix.lower() in _IMG_EXTS:
                img = zf.read(name)
                if len(img) >= _MIN_IMAGE_BYTES:
                    images.append(img)
    return images


def extract_docx_pages_as_images(file_bytes: bytes) -> list[bytes]:
    """
    Rasterizes DOCX pages to PNG for Claude Vision to read visual content.

    When the DOCX has low text density (EMF-heavy documents), also extracts
    and converts the EMF/WMF files from word/media/ so Claude can read table
    and chart data that is not accessible via text extraction.

    Distinct from extract_images_from_file(), which extracts inline images
    for decorative use in slides (assigned via imagen_idx in the outline).
    """
    return _extract_pages_from_docx_as_images(file_bytes)


def extract_emf_text_from_docx(file_bytes: bytes) -> str:
    """
    Extrae texto de imágenes EMF/WMF embebidas en un DOCX.

    Los EMF almacenan texto en UTF-16-LE. Esta función lee los bytes
    directamente sin dependencias externas, recuperando el contenido
    de tablas que no aparecen en la extracción de texto normal (mammoth).

    Returns:
        Texto extraído de todos los EMF del documento, concatenado.
        String vacío si no hay EMF o si la extracción falla.
    """
    resultado = []
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            emf_files = [
                name for name in zf.namelist()
                if name.startswith("word/media/")
                and name.lower().endswith((".emf", ".wmf"))
            ]
            for name in sorted(emf_files):
                emf_bytes = zf.read(name)
                texto = _leer_texto_utf16_emf(emf_bytes)
                if texto.strip():
                    resultado.append(texto)
    except Exception:
        pass
    return "\n".join(resultado)


def _leer_texto_utf16_emf(emf_bytes: bytes) -> str:
    """
    Lee texto en codificación UTF-16-LE de un archivo EMF/WMF.

    Decodifica cada par de bytes como code point UTF-16-LE y conserva los
    caracteres imprimibles (cp >= 0x20, sin controles ni separadores raros),
    recuperando acentos y ñ además del ASCII. Los bytes de estructura EMF
    (coordenadas, tamaños) decodifican a símbolos sueltos o runs cortos que
    se descartan por los guardas anti-ruido: cada run conserva solo si tiene
    >=3 caracteres, al menos 2 letras latinas y mayoría de letras latinas
    (ratio >= 0.5). Se cuentan solo letras latinas (no CJK ni símbolos) para
    que ampliar el rango a Unicode imprimible no deje pasar basura binaria
    (bytes de estructura EMF que decodifican a ideogramas u otros signos).

    El resultado se emite como UNA celda/run por línea, precedido de un
    encabezado con el conteo. Son celdas/runs sueltas, NO filas exactas: la
    grilla original (qué celda pertenece a qué fila) no es recuperable del EMF
    por este método y queda como deuda futura (parser de grilla real).

    Returns:
        Bloque '[TABLA: N celdas detectadas ...]' seguido de una celda por
        línea, o string vacío si no se detecta ninguna celda con texto.
    """
    runs: list[str] = []
    current: list[str] = []

    def _flush() -> None:
        s = ''.join(current).strip()
        latinas = sum(
            unicodedata.name(c, "").startswith("LATIN") for c in s
        )
        if len(s) >= 3 and latinas >= 2 and latinas / len(s) >= 0.5:
            runs.append(s)

    i = 0
    while i < len(emf_bytes) - 1:
        cp = int.from_bytes(emf_bytes[i:i + 2], "little")
        ch = chr(cp)
        if cp >= 0x20 and ch.isprintable():
            current.append(ch)
        else:
            _flush()
            current = []
        i += 2
    _flush()

    if not runs:
        return ""
    encabezado = (
        f"[TABLA: {len(runs)} celdas detectadas "
        "(celdas/runs sueltas, no filas exactas)]"
    )
    return encabezado + "\n" + "\n".join(runs)
