from services.extraction_service import ExtractionService
from services.ai_service import AIService
from services.pptx_service import PPTXService
from services.gamma_service import GammaService
from repositories.generation_repo import GenerationRepo

# Orquesta el pipeline completo:
# extraction → ai → pptx → gamma → persistencia en DB
# Es el único punto de entrada al pipeline; no llamar a los sub-servicios directamente
