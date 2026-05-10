from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class GenerationStatus(str, Enum):
    procesando = "procesando"
    listo = "listo"
    error = "error"


class TemplateEnum(str, Enum):
    ejecutivo_oscuro = "ejecutivo_oscuro"
    profesional_claro = "profesional_claro"
    corporativo_neutro = "corporativo_neutro"


class ToneEnum(str, Enum):
    formal = "formal"
    institucional = "institucional"
    comercial = "comercial"
    tecnico = "tecnico"


class AudienceEnum(str, Enum):
    directivos = "directivos"
    equipo_interno = "equipo_interno"
    clientes = "clientes"
    tecnicos = "tecnicos"


class OutputEnum(str, Enum):
    pptx = "pptx"
    gamma = "gamma"
    ambos = "ambos"


class TemaVisualEnum(str, Enum):
    minimalist = "minimalist"
    playful = "playful"
    organic = "organic"
    modular = "modular"
    elegant = "elegant"
    digital = "digital"
    geometric = "geometric"


class EstiloImagenEnum(str, Enum):
    aiGenerated = "aiGenerated"
    webAllImages = "webAllImages"
    webFreeToUse = "webFreeToUse"
    webFreeToUseCommercially = "webFreeToUseCommercially"
    pictographic = "pictographic"
    giphy = "giphy"
    pexels = "pexels"
    placeholder = "placeholder"
    noImages = "noImages"


class GenerationRequest(BaseModel):
    archivos: list[str] = Field(min_length=1, max_length=10)
    objetivo: str = Field(min_length=10, max_length=500)
    informacion_adicional: str | None = Field(default=None, max_length=1000)
    template: TemplateEnum
    tono: ToneEnum
    audiencia: AudienceEnum
    output: OutputEnum = OutputEnum.ambos
    usar_imagenes_documento: bool = False
    tema_visual: TemaVisualEnum = TemaVisualEnum.minimalist
    estilo_imagen: EstiloImagenEnum = EstiloImagenEnum.aiGenerated
    paleta_colores: str = ""
    cantidad_slides: int = Field(default=10, ge=5, le=20)

    @field_validator("objetivo", "informacion_adicional")
    @classmethod
    def sanitize_text(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = re.sub(r"[<>\"']", "", v)
        return v.strip()

    @field_validator("archivos")
    @classmethod
    def sanitize_filenames(cls, v: list[str]) -> list[str]:
        cleaned = [re.sub(r"[<>\"'|\\/*?]", "", name).strip() for name in v]
        if not all(cleaned):
            raise ValueError("Los nombres de archivo no pueden estar vacíos.")
        return cleaned


class GenerationResponse(BaseModel):
    id: str
    usuario_id: str
    objetivo: str
    estado: GenerationStatus
    pptx_url: str | None = None
    gamma_url: str | None = None
    pptx_gamma_url: str | None = None
    slides_count: int | None = None
    creado_en: str
