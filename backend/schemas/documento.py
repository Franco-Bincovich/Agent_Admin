from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Las 7 secciones válidas que puede incluir un documento generado.
DocumentoSeccion = Literal[
    "resumen_ejecutivo",
    "introduccion",
    "analisis",
    "conclusiones",
    "recomendaciones",
    "anexos",
    "glosario",
]


class DocumentoOpciones(BaseModel):
    homogeneizar: bool = False
    deduplicar: bool = False
    usar_imagenes: bool = False


class CreateDocumentoRequest(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    secciones: list[DocumentoSeccion] = Field(default=[])
    indicaciones: str | None = Field(default=None, max_length=1000)
    opciones: DocumentoOpciones = Field(default_factory=DocumentoOpciones)

    @field_validator("titulo")
    @classmethod
    def sanitize_titulo(cls, v: str) -> str:
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()

    @field_validator("indicaciones")
    @classmethod
    def sanitize_indicaciones(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r'[<>"\']', "", v)
        return v.strip()


class DocumentoResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    usuario_id: str
    titulo: str
    estado: str
    documento_url: str | None = Field(None, alias="docx_url")
    creado_en: str
