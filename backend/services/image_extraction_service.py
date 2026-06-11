from __future__ import annotations

import io
import os
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
    Combines rasterized pages and inline images from a DOCX.

    Pages are returned first so Claude reads table/chart content before
    decorative inline images. Inline images are filtered to PNG/JPG/JPEG/GIF.
    """
    _SUPPORTED = {".png", ".jpg", ".jpeg", ".gif"}
    pages = _extract_pages_from_docx_as_images(file_bytes)
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
    return pages + inline


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
