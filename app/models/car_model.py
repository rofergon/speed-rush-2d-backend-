from enum import Enum
from pydantic import BaseModel
from typing import List

class CarStyle(str, Enum):
    PIXEL_ART = "pixel_art"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    MINIMALIST = "minimalist"

class PartType(str, Enum):
    ENGINE = "ENGINE"
    TRANSMISSION = "TRANSMISSION"
    WHEELS = "WHEELS"

class CarPart(BaseModel):
    partType: PartType
    stat1: int
    stat2: int
    stat3: int
    imageURI: str

    class Config:
        use_enum_values = True

class CarConfig(BaseModel):
    style: CarStyle = CarStyle.CARTOON
    engineType: str = "standard"
    transmissionType: str = "manual"
    wheelsType: str = "sport"

    class Config:
        use_enum_values = True

class CarGenerationResponse(BaseModel):
    carImageURI: str
    parts: List[CarPart]

    class Config:
        use_enum_values = True
