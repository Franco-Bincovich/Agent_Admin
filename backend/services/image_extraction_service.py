from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import fitz

_MIN_IMAGE_BYTES = 5 * 1024  # 5 KB — filtra solo íconos muy pequeños


def extract_images_from_file(filename: str, file_bytes: bytes) -> list[bytes]:
    """
    Extrae las imágenes embebidas de un archivo, detectando el tipo por extensión.

    Soporta los siguientes formatos:
    - .pdf  → PyMuPDF: extrae imágenes página por página usando get_images().
    - .docx → recorre el zip interno y extrae archivos de word/media/.
    - .xlsx → no soporta imágenes; retorna [] sin error.

    Si ocurre cualquier fallo durante la extracción, retorna [] para no
    bloquear el pipeline principal.
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
    """Extrae imágenes de cada página de un PDF usando PyMuPDF."""
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


def _emf_to_png(emf_bytes: bytes) -> bytes | None:
    """
    Convierte imagen EMF o WMF a PNG usando PyMuPDF.
    Devuelve los bytes PNG, o None si la conversión falla.
    """
    try:
        doc = fitz.open(stream=emf_bytes, filetype="emf")
        page = doc[0]
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        png_bytes = pix.tobytes("png")
        doc.close()
        return png_bytes
    except Exception:
        return None


def _extract_images_from_docx(file_bytes: bytes) -> list[bytes]:
    """
    Extrae imágenes del directorio word/media/ dentro del ZIP de un DOCX.
    Convierte EMF/WMF a PNG con PyMuPDF antes de incluirlos.
    Descarta formatos no soportados por la API de Anthropic.
    """
    _SUPPORTED = {".png", ".jpg", ".jpeg", ".gif"}
    _CONVERT = {".emf", ".wmf"}
    images: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if not name.startswith("word/media/"):
                continue
            ext = os.path.splitext(name)[1].lower()
            img = zf.read(name)
            if len(img) < _MIN_IMAGE_BYTES:
                continue
            if ext in _SUPPORTED:
                images.append(img)
            elif ext in _CONVERT:
                png = _emf_to_png(img)
                if png:
                    images.append(png)
    return images


def _extract_images_from_xlsx(file_bytes: bytes) -> list[bytes]:
    """Extrae imágenes del directorio xl/media/ dentro del ZIP de un XLSX."""
    _IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    images: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if name.startswith("xl/media/") and Path(name).suffix.lower() in _IMG_EXTS:
                img = zf.read(name)
                if len(img) >= _MIN_IMAGE_BYTES:
                    images.append(img)
    return images
