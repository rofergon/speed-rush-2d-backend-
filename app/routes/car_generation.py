from fastapi import APIRouter, HTTPException
from ..models.car_model import CarGenerationRequest, CarGenerationResponse
from ..services.image_generation_service import ImageGenerationService

router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate", response_model=CarGenerationResponse)
async def generate_car(request: CarGenerationRequest):
    try:
        # Generar el sprite del carro y obtener la URL
        image_url = await image_service.generate_car_sprite(request.prompt)
        
        return CarGenerationResponse(
            success=True,
            message="URL de imagen generada exitosamente",
            image_url=image_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
