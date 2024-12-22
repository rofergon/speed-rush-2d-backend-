from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from ..models.car_model import CarGenerationRequest
from ..services.image_generation_service import ImageGenerationService

router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate")
async def generate_car(request: CarGenerationRequest):
    try:
        # Generar el sprite del carro y obtener la imagen como bytes
        image_bytes = await image_service.generate_car_sprite(request.prompt)
        
        # Crear un objeto BytesIO con los bytes de la imagen
        image_stream = BytesIO(image_bytes)
        image_stream.seek(0)
        
        # Devolver la imagen como respuesta streaming
        return StreamingResponse(
            content=image_stream,
            media_type="image/png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
