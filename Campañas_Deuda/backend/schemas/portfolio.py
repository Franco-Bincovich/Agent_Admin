from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PortfolioUploadResponse(BaseModel):
    id: UUID
    filename: str
    cartera: str
    size_bytes: int
    uploaded_at: datetime


class PortfolioFileResponse(BaseModel):
    id: UUID
    filename: str
    cartera: str
    dureza: str
    periodo: str
    size_bytes: int
    uploaded_by: UUID
    uploaded_at: datetime
    # Agregados parseados del archivo (disponibles después del procesamiento)
    monto_total: float
    cantidad_partidas: int
