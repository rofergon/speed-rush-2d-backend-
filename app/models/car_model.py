from pydantic import BaseModel

class CarGenerationRequest(BaseModel):
    prompt: str
    
class CarGenerationResponse(BaseModel):
    success: bool
    message: str
    image_url: str | None = None
