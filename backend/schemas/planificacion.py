from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Prioridad(str, Enum):
    alta = "alta"
    media = "media"
    baja = "baja"


class OrigenArchivo(str, Enum):
    excel = "excel"
    mpp = "mpp"
    pdf = "pdf"


class PlanificacionEstado(str, Enum):
    procesando = "procesando"
    listo = "listo"
    error = "error"


class Confianza(str, Enum):
    alta = "alta"
    media = "media"
    baja = "baja"


class ProyectoCreateRequest(BaseModel):
    nombre: str = Field(min_length=3, max_length=200)
    expediente: str | None = Field(default=None, max_length=100)
    prioridad: Prioridad = Prioridad.media

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()

    @field_validator("expediente")
    @classmethod
    def sanitize_expediente(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()


class ProyectoResponse(BaseModel):
    id: str
    usuario_id: str
    nombre: str
    expediente: str | None = None
    prioridad: str
    origen: str | None = None
    archivo_url: str | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    estado: PlanificacionEstado
    error_detalle: str | None = None
    creado_en: str
    actualizado_en: str | None = None


class AreaCreateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    cap_wbs: str | None = Field(default=None, max_length=20)
    color: str | None = Field(default=None, max_length=7)
    responsable_nombre: str | None = Field(default=None, max_length=200)
    responsable_telefono: str | None = Field(default=None, max_length=50)
    responsable_email: str | None = Field(default=None, max_length=254)
    disponibilidad_horas: int | None = Field(default=None, ge=0)
    cantidad_empleados: int | None = Field(default=None, ge=0)

    @field_validator("cap_wbs")
    @classmethod
    def validate_cap_wbs(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[\d.]+$", v):
            raise ValueError("El WBS solo puede contener dígitos y puntos.")
        return v

    @field_validator("nombre", "responsable_nombre")
    @classmethod
    def sanitize_text(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()

    @field_validator("responsable_email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("El email del responsable no tiene un formato válido.")
        return v.lower().strip()


class AreaUpdateRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    responsable_nombre: str | None = Field(default=None, max_length=200)
    responsable_telefono: str | None = Field(default=None, max_length=50)
    responsable_email: str | None = Field(default=None, max_length=254)
    disponibilidad_horas: int | None = Field(default=None, ge=0)
    cantidad_empleados: int | None = Field(default=None, ge=0)

    @field_validator("nombre", "responsable_nombre")
    @classmethod
    def sanitize_text(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()

    @field_validator("responsable_email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("El email del responsable no tiene un formato válido.")
        return v.lower().strip()


class AreaResponse(BaseModel):
    id: str
    proyecto_id: str
    nombre: str
    cap_wbs: str | None = None
    color: str | None = None
    responsable_nombre: str | None = None
    responsable_telefono: str | None = None
    responsable_email: str | None = None
    disponibilidad_horas: int | None = None
    cantidad_empleados: int | None = None
    creado_en: str


class TareaResponse(BaseModel):
    id: str
    proyecto_id: str
    area_id: str | None = None
    wbs: str
    nombre: str
    nivel: int
    es_resumen: bool
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    fecha_estimada: bool
    confianza: str
    predecesoras: str | None = None
    completada: bool
    completada_en: str | None = None
    completada_por: str | None = None
    creado_en: str


class MarcarTareaRequest(BaseModel):
    completada: bool


class AreaAsignacionRequest(BaseModel):
    area_id: str | None = None


class ProyectoDetalleResponse(ProyectoResponse):
    areas: list[AreaResponse] = Field(default_factory=list)
    tareas: list[TareaResponse] = Field(default_factory=list)
