from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
import base64
from ..models.car_model import CarGenerationRequest, CarGenerationResponse, CarTraits
from ..services.image_generation_service import ImageGenerationService

router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate")
async def generate_car(request: CarGenerationRequest):
    try:
        # Generar el sprite del carro y obtener la imagen como bytes junto con los traits
        image_bytes, traits = await image_service.generate_car_sprite(request.prompt)
        
        # Convertir la imagen a base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
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
        
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
