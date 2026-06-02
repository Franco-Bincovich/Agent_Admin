from uuid import UUID

from fastapi import UploadFile

from schemas.portfolio import PortfolioFileResponse, PortfolioUploadResponse
from utils.errors import AppError


async def upload_portfolio(file: UploadFile) -> PortfolioUploadResponse:
    """
    Valida y persiste un archivo de cartera.

    Acepta CSV, XLSX o PDF. Valida tipo MIME y tamaño. Extrae los
    agregados del archivo y los almacena junto con los metadatos.

    Args:
        file: Archivo de cartera subido via multipart/form-data.

    Returns:
        PortfolioUploadResponse con el ID y metadatos del archivo.

    Raises:
        AppError: "INVALID_FILE_TYPE" (422) si el tipo no es válido.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def list_portfolios() -> list[PortfolioFileResponse]:
    """
    Lista los archivos de cartera del usuario autenticado.

    Returns:
        Lista de PortfolioFileResponse.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def get_portfolio(portfolio_id: UUID) -> PortfolioFileResponse:
    """
    Devuelve el detalle de un archivo de cartera.

    Args:
        portfolio_id: UUID del archivo.

    Returns:
        PortfolioFileResponse con agregados incluidos.

    Raises:
        AppError: "NOT_FOUND" (404) si no existe o no pertenece al usuario.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
