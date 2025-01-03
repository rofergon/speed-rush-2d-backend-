from fastapi import APIRouter, HTTPException
from ..services.image_generation_service import ImageGenerationService
from ..services.cache_service import CacheService
from ..models.car_model import CarConfig
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Instanciar servicios
image_service = ImageGenerationService()
cache_service = CacheService()

@router.post("/generate")
async def generate_car(config: CarConfig):
    """
    Genera o retorna un carro pre-generado con sus componentes.
    Si hay una respuesta en caché, la retorna y elimina.
    Si no hay caché, genera una nueva respuesta.
    """
    try:
        # Intentar obtener una respuesta pre-generada
        cached_response = cache_service.get_cached_response()
        if cached_response:
            logger.info("Retornando respuesta pre-generada del caché")
            return cached_response
            
        # Si no hay caché, generar nueva respuesta
        logger.info("No hay caché disponible, generando nueva respuesta")
        response = await image_service.generate_car_assets(config)
        return response
        
    except Exception as e:
        logger.error(f"Error en generate_car: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando carro: {str(e)}"
        )

@router.post("/pregenerate")
async def pregenerate_car(config: CarConfig):
    """
    Endpoint administrativo para pre-generar y almacenar respuestas.
    """
    try:
        # Generar nueva respuesta
        response = await image_service.generate_car_assets(config)
        
        # Guardar en caché
        cache_id = cache_service.save_response(response)
        
        return {
            "message": "Respuesta pre-generada y almacenada exitosamente",
            "cache_id": cache_id
        }
        
    except Exception as e:
        logger.error(f"Error en pregenerate_car: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error pre-generando carro: {str(e)}"
        )
