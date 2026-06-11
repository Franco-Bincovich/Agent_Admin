from uuid import UUID

from fastapi import APIRouter, UploadFile

from controllers import portfolio_controller
from schemas.portfolio import PortfolioFileResponse, PortfolioUploadResponse

router = APIRouter()


@router.post("/upload", response_model=PortfolioUploadResponse, status_code=201)
async def upload_portfolio(file: UploadFile) -> PortfolioUploadResponse:
    """
    Carga de archivo de cartera (CSV/XLSX/PDF).
    Stub — implementar en Sesión 5.
    """
    return await portfolio_controller.upload_portfolio(file)


@router.get("/", response_model=list[PortfolioFileResponse])
async def list_portfolios() -> list[PortfolioFileResponse]:
    """Listar archivos de cartera cargados. Stub — implementar en Sesión 5."""
    return await portfolio_controller.list_portfolios()


@router.get("/{portfolio_id}", response_model=PortfolioFileResponse)
async def get_portfolio(portfolio_id: UUID) -> PortfolioFileResponse:
    """Detalle de un archivo de cartera. Stub — implementar en Sesión 5."""
    return await portfolio_controller.get_portfolio(portfolio_id)
