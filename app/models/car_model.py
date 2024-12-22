from pydantic import BaseModel
from enum import Enum

class CarStyle(str, Enum):
    PIXEL_ART = "pixel_art"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    MINIMALIST = "minimalist"

class CarGenerationRequest(BaseModel):
    prompt: str
    style: CarStyle = CarStyle.CARTOON  # Por defecto será estilo cartoon
