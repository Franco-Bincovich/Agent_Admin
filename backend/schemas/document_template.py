from __future__ import annotations

import json as _json
import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SeccionItemSchema(BaseModel):
    id: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()

    @field_validator("descripcion")
    @classmethod
    def sanitize_descripcion(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r'[<>"\']', '', v)
        return v.strip() or None


class CreateTemplateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    secciones: list[SeccionItemSchema] = Field(min_length=1)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()

    @field_validator("secciones")
    @classmethod
    def validate_secciones(cls, v: list[SeccionItemSchema]) -> list[SeccionItemSchema]:
        filtered = [s for s in v if s.nombre.strip()]
        if not filtered:
            raise ValueError("Debe incluir al menos una sección")
        return filtered


class UpdateTemplateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    secciones: list[SeccionItemSchema] = Field(min_length=1)
    is_default: bool = False

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()

    @field_validator("secciones")
    @classmethod
    def validate_secciones(cls, v: list[SeccionItemSchema]) -> list[SeccionItemSchema]:
        filtered = [s for s in v if s.nombre.strip()]
        if not filtered:
            raise ValueError("Debe incluir al menos una sección")
        return filtered


def _parse_secciones(raw) -> list:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            return _json.loads(raw)
        except Exception:
            return []
    return []


class TemplateResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    nombre: str
    secciones: list[dict]
    is_default: bool
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def from_db(cls, data: dict) -> "TemplateResponse":
        return cls(
            id=data["id"],
            usuario_id=data["usuario_id"],
            nombre=data["nombre"],
            secciones=_parse_secciones(data.get("secciones", [])),
            is_default=data.get("is_default", False),
            creado_en=data["creado_en"],
            actualizado_en=data["actualizado_en"],
        )
