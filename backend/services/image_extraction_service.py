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
    - .docx → rasteriza páginas completas con PyMuPDF (captura EMF/WMF embebidos)
              más imágenes inline de word/media/.
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


def _extract_pages_from_docx_as_images(file_bytes: bytes) -> list[bytes]:
    """
    Abre el DOCX con PyMuPDF y rasteriza cada página a PNG.
    Captura el contenido visual completo incluyendo tablas como imágenes
    vectoriales (EMF/WMF) que no son accesibles por extracción de texto.
    Devuelve lista de PNG bytes. Retorna lista vacía si falla.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="docx")
        images = []
        for page in doc:
            mat = fitz.Matrix(150 / 72, 150 / 72)  # 150 DPI
            pix = page.get_pixmap(matrix=mat)
            images.append(pix.tobytes("png"))
        doc.close()
        return images
    except Exception:
        return []


def _extract_images_from_docx(file_bytes: bytes) -> list[bytes]:
    """
    Combina dos fuentes de imágenes de un DOCX:
    1. Páginas rasterizadas completas via PyMuPDF (captura tablas EMF/WMF embebidas).
    2. Imágenes inline de word/media/ (.png/.jpg/.jpeg/.gif).
    Las páginas se entregan primero para que Claude Vision lea tablas antes que
    las imágenes sueltas.
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
