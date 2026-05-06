import io
import zipfile
from pathlib import Path

import fitz
import mammoth
import openpyxl

from utils.errors import AppError, ErrorCode

MIN_TEXT_LENGTH = 50


def _extract_from_pdf(file_bytes: bytes) -> str:
    """Extrae texto de un PDF página por página usando PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def _extract_from_docx(file_bytes: bytes) -> str:
    """Extrae texto plano de un DOCX conservando la estructura de párrafos."""
    result = mammoth.extract_raw_text(io.BytesIO(file_bytes))
    return result.value


def _extract_from_txt(file_bytes: bytes) -> str:
    """Decodifica un archivo TXT con fallback de utf-8 a latin-1."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def _extract_from_xlsx(file_bytes: bytes) -> str:
    """Extrae texto de todas las hojas de un XLSX, celda por celda."""
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    rows: list[str] = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            cells = [str(cell) for cell in row if cell is not None]
            if cells:
                rows.append("\t".join(cells))
    return "\n".join(rows)


_EXTRACTORS = {
    ".pdf": _extract_from_pdf,
    ".docx": _extract_from_docx,
    ".txt": _extract_from_txt,
    ".xlsx": _extract_from_xlsx,
}


def extract_images_from_file(filename: str, file_bytes: bytes) -> list[bytes]:
    """
    Extrae las imágenes embebidas de un archivo, detectando el tipo por extensión.

    Soporta los siguientes formatos:
    - .pdf  → PyMuPDF: extrae imágenes página por página usando get_images().
    - .docx → python-docx: recorre el zip interno y extrae archivos de word/media/.
    - .xlsx → no soporta imágenes; retorna [] sin error.

    Las imágenes son opcionales dentro del pipeline de generación de documentos.
    Si ocurre cualquier fallo durante la extracción, la función retorna [] en lugar
    de lanzar una excepción, para no bloquear el pipeline principal.

    Args:
        filename: Nombre del archivo con su extensión (ej. 'informe.pdf').
        file_bytes: Contenido binario del archivo.

    Returns:
        Lista de bytes, uno por imagen encontrada. Puede ser vacía si no hay
        imágenes, si el formato no las soporta, o si ocurre un error interno.
    """
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".pdf":
            return _extract_images_from_pdf(file_bytes)
        if ext == ".docx":
            return _extract_images_from_docx(file_bytes)
        # .xlsx y formatos no reconocidos no contienen imágenes accesibles.
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


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """
    Extrae texto plano de un archivo, detectando el tipo por extensión.

    Delega a la función específica según la extensión y valida que el
    resultado contenga contenido útil (mínimo 50 caracteres).

    Args:
        filename: Nombre del archivo con su extensión (ej. 'informe.pdf').
        file_bytes: Contenido binario del archivo.

    Returns:
        Texto extraído, limpio y sin espacios extremos.

    Raises:
        AppError: code 'UNSUPPORTED_FORMAT', status 400 si la extensión no está soportada.
        AppError: code 'EMPTY_FILE', status 422 si el texto tiene menos de 50 caracteres.
    """
    ext = Path(filename).suffix.lower()
    extractor = _EXTRACTORS.get(ext)
    if not extractor:
        raise AppError(
            f"Formato no soportado: '{ext}'. Formatos válidos: pdf, docx, txt, xlsx.",
            ErrorCode.UNSUPPORTED_FORMAT,
            400,
        )
    text = extractor(file_bytes)
    if len(text.strip()) < MIN_TEXT_LENGTH:
        raise AppError(
            "El archivo no contiene texto suficiente.",
            ErrorCode.EMPTY_FILE,
            422,
        )
    return text.strip()
