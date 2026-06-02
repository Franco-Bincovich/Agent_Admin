from uuid import UUID

from schemas.portfolio import PortfolioFileResponse
from utils.errors import AppError


async def save(portfolio_data: dict) -> PortfolioFileResponse:
    """
    Persiste los metadatos de un archivo de cartera.

    Args:
        portfolio_data: Metadatos y agregados del archivo procesado.

    Returns:
        PortfolioFileResponse con el ID asignado.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def find_by_id(portfolio_id: UUID) -> PortfolioFileResponse | None:
    """
    Busca un archivo de cartera por ID.

    Args:
        portfolio_id: UUID del archivo.

    Returns:
        PortfolioFileResponse o None.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def find_all_by_user(user_id: UUID) -> list[PortfolioFileResponse]:
    """
    Devuelve todos los archivos de cartera del usuario.

    Args:
        user_id: UUID del usuario.

    Returns:
        Lista de PortfolioFileResponse.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 5.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
