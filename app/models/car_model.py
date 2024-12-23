from pydantic import BaseModel
from enum import Enum

class CarStyle(str, Enum):
    PIXEL_ART = "pixel_art"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    MINIMALIST = "minimalist"

class CarTraits(BaseModel):
    speed: int  # 1-10
    acceleration: int  # 1-10
    handling: int  # 1-10
    drift_factor: int  # 1-10
    turn_factor: int  # 1-10
    max_speed: int  # 1-10

class CarGenerationRequest(BaseModel):
    prompt: str
    style: CarStyle = CarStyle.CARTOON  # Por defecto será estilo cartoon

class CarGenerationResponse(BaseModel):
    image_data: bytes
    traits: CarTraits
