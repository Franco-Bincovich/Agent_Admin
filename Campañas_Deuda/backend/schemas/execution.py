from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

Cartera = Literal["servicios_generales", "servicio_sanitario", "automotor", "todas"]
Dureza = Literal["blanda", "intermedia", "dura", "todas"]
EstadoEjecucion = Literal["pendiente", "corriendo", "listo", "error"]


class ExecutionCreate(BaseModel):
    portfolio_file_id: UUID
    cartera: Cartera
    dureza: Dureza
    periodo: str  # "2021" | "2022" | ... | "2026" | "todas"


class ExecutionStatus(BaseModel):
    id: UUID
    estado: EstadoEjecucion
    portfolio_file_id: UUID
    cartera: str
    dureza: str
    periodo: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None


class ExecutionResponse(ExecutionStatus):
    """Respuesta completa con el resultado final de la ejecución."""

    resultado_url: str | None = None  # URL del .docx generado
    created_by: UUID
