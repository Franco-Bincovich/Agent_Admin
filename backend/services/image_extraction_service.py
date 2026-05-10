from __future__ import annotations

import io
import zipfile
from pathlib import Path

import fitz


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
            images.append(base_image["image"])
    doc.close()
    return images


def _extract_images_from_docx(file_bytes: bytes) -> list[bytes]:
    """Extrae imágenes del directorio word/media/ dentro del ZIP de un DOCX."""
    images: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                images.append(zf.read(name))
    return images


def _extract_images_from_xlsx(file_bytes: bytes) -> list[bytes]:
    """Extrae imágenes del directorio xl/media/ dentro del ZIP de un XLSX."""
    _IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    images: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        for name in zf.namelist():
            if name.startswith("xl/media/") and Path(name).suffix.lower() in _IMG_EXTS:
                images.append(zf.read(name))
    return images
