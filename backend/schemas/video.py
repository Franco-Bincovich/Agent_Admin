from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class VideoJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class EstiloEdicion(str, Enum):
    dinamico = "dinamico"
    corporativo = "corporativo"
    minimalista = "minimalista"


class FormatoSalida(str, Enum):
    horizontal_16_9 = "horizontal_16_9"
    vertical_9_16 = "vertical_9_16"
    cuadrado_1_1 = "cuadrado_1_1"


class PosicionSubtitulos(str, Enum):
    abajo = "abajo"
    centro = "centro"
    arriba = "arriba"
    sin_subtitulos = "sin_subtitulos"


class ResolucionVideo(str, Enum):
    hd_720p = "hd_720p"
    full_hd_1080p = "full_hd_1080p"
    ultra_hd_4k = "ultra_hd_4k"


class VarianteConfig(BaseModel):
    estilo: EstiloEdicion
    formato: FormatoSalida
    posicion_subtitulos: PosicionSubtitulos
    resolucion: ResolucionVideo


class CreateVideoJobRequest(BaseModel):
    titulo: str = Field(..., max_length=200)
    variantes: list[VarianteConfig] = Field(..., min_length=1, max_length=5)


class VideoJobResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    usuario_id: str
    titulo: str | None = None
    estado: VideoJobStatus
    video_input_url: str | None = None
    output_url: str | None = None
    parametros: dict = Field(default_factory=dict)
    error_message: str | None = None
    creado_en: str
