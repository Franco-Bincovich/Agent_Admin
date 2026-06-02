from uuid import UUID

from fastapi import UploadFile

from schemas.portfolio import PortfolioFileResponse, PortfolioUploadResponse
from utils.errors import AppError

ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/pdf",
}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB para archivos de cartera


async def upload_and_parse(file: UploadFile, uploaded_by: UUID) -> PortfolioUploadResponse:
    """
    Valida el archivo de cartera y extrae los agregados.

    Acepta CSV, XLSX o PDF. Valida tipo MIME real (no solo la extensión)
    y tamaño. Extrae totales agregados (monto, partidas, distribución) que
    recibirá el Agente 1 — nunca datos de deudores individuales.

    Args:
        file: Archivo subido via multipart/form-data.
        uploaded_by: UUID del usuario que sube el archivo.

    Returns:
        PortfolioUploadResponse con ID y metadatos.

    Raises:
        AppError: "INVALID_FILE_TYPE" (422) si el tipo no está en ALLOWED_MIME_TYPES.
        AppError: "FILE_TOO_LARGE" (413) si supera MAX_FILE_SIZE_BYTES.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def get_portfolio(portfolio_id: UUID, user_id: UUID) -> PortfolioFileResponse:
    """
    Devuelve el detalle de un archivo de cartera verificando ownership.

    Args:
        portfolio_id: UUID del archivo.
        user_id: UUID del usuario solicitante (para verificar ownership).

    Returns:
        PortfolioFileResponse con agregados.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe o no pertenece al usuario.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
