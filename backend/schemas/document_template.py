from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CreateTemplateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    secciones: list[str] = Field(min_length=1)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()

    @field_validator("secciones")
    @classmethod
    def validate_secciones(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Debe incluir al menos una sección")
        return [s.strip() for s in v if s.strip()]


class UpdateTemplateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    secciones: list[str] = Field(min_length=1)
    is_default: bool = False

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()


class TemplateResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    nombre: str
    secciones: list[str]
    is_default: bool
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def from_db(cls, data: dict) -> "TemplateResponse":
        return cls(
            id=data["id"],
            usuario_id=data["usuario_id"],
            nombre=data["nombre"],
            secciones=data["secciones"] if isinstance(data["secciones"], list) else [],
            is_default=data.get("is_default", False),
            creado_en=data["creado_en"],
            actualizado_en=data["actualizado_en"],
        )
