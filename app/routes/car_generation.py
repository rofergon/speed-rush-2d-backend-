from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from ..models.car_model import CarGenerationRequest, CarGenerationResponse, CarConfig
from ..services.image_generation_service import ImageGenerationService

logger = logging.getLogger(__name__)
router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate")
async def generate_car(request: CarGenerationRequest) -> CarGenerationResponse:
    try:
        logger.info(f"Iniciando generación de carro con prompt: {request.prompt}")
        
        # Crear configuración del carro
        config = CarConfig(
            basePrompt=request.prompt,
            style=request.style,
            engineType="performance",  # Podríamos hacer esto configurable
            transmissionType="automatic",
            wheelsType="racing"
        )
        
        # Generar assets del carro
        result = await image_service.generate_car_assets(config)
        logger.info("Assets generados exitosamente")
        
        return CarGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error en la generación del carro: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "Error en la generación del carro", "error": str(e)}
        )
