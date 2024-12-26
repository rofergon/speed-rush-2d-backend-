from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class CarStyle(str, Enum):
    PIXEL_ART = "pixel_art"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    MINIMALIST = "minimalist"

class PartType(int, Enum):
    ENGINE = 0
    TRANSMISSION = 1
    WHEELS = 2

class CarPart(BaseModel):
    partType: PartType
    stat1: int = Field(..., ge=1, le=10, description="Primera estadística de la parte")
    stat2: int = Field(..., ge=1, le=10, description="Segunda estadística de la parte")
    stat3: int = Field(..., ge=1, le=10, description="Tercera estadística de la parte")
    imageURI: str = Field(..., description="URI de IPFS donde está almacenada la imagen")

class CarGenerationRequest(BaseModel):
    prompt: str
    style: CarStyle = CarStyle.CARTOON
    engineType: str = "standard"
    transmissionType: str = "manual"
    wheelsType: str = "sport"

class CarGenerationResponse(BaseModel):
    carImageURI: str
    parts: List[CarPart]

class CarConfig(BaseModel):
    engineType: str
    transmissionType: str
    wheelsType: str
    style: CarStyle = CarStyle.CARTOON
    basePrompt: str
