from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
import base64
import logging
from ..models.car_model import CarGenerationRequest, CarGenerationResponse, CarTraits
from ..services.image_generation_service import ImageGenerationService

logger = logging.getLogger(__name__)
router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate")
async def generate_car(request: CarGenerationRequest):
    try:
        logger.info(f"Iniciando generación de carro con prompt: {request.prompt}")
        
        # Generar el sprite del carro y obtener la imagen como bytes junto con los traits
        image_bytes, traits = await image_service.generate_car_sprite(request.prompt)
        logger.info("Imagen generada exitosamente")
        
        # Convertir la imagen a base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        logger.info("Imagen convertida a base64")
        
        # Crear la respuesta con la imagen y los metadatos
        response = {
            "image": {
                "data": base64_image,
                "content_type": "image/png",
                "filename": "car_sprite.png"
            },
            "metadata": {
                "traits": {
                    "speed": traits.speed,
                    "acceleration": traits.acceleration,
                    "handling": traits.handling,
                    "drift_factor": traits.drift_factor,
                    "turn_factor": traits.turn_factor,
                    "max_speed": traits.max_speed
                }
            }
        }
        
        logger.info("Respuesta preparada exitosamente")
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error en la generación del carro: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={"message": "Error en la generación del carro", "error": str(e)}
        )
