from .stability_service import StabilityService
from .lighthouse_service import LighthouseService
import requests
from io import BytesIO
from rembg import remove, new_session
from PIL import Image
import os
import random
from ..models.car_model import CarPart, PartType, CarConfig
import logging
import glob

logger = logging.getLogger(__name__)

class ImageGenerationService:
    def __init__(self):
        self.stability_service = StabilityService()
        self.lighthouse_service = LighthouseService()
        logger.info("Iniciando carga del modelo rembg...")
        try:
            self.rembg_session = new_session()
            logger.info("Modelo rembg cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando modelo rembg: {str(e)}")
            self.rembg_session = None
        
        # Obtener todas las imágenes de referencia
        self.base_images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
        self.base_images = [f for f in glob.glob(os.path.join(self.base_images_dir, "*.png")) 
                          if os.path.basename(f).startswith("car")]
        if not self.base_images:
            raise Exception("No se encontraron imágenes de referencia en assets/")
        logger.info(f"Imágenes de referencia encontradas: {len(self.base_images)}")

    def _get_random_base_image(self) -> str:
        """Selecciona una imagen de referencia aleatoria."""
        selected_image = random.choice(self.base_images)
        logger.info(f"Usando imagen de referencia: {os.path.basename(selected_image)}")
        return selected_image

    def _calculate_part_stats(self, part_type: PartType, config: CarConfig) -> tuple[int, int, int]:
        """Calcula las estadísticas para una parte específica."""
        if part_type == PartType.ENGINE:
            return (
                random.randint(5, 10),  # Potencia
                random.randint(3, 8),   # Eficiencia
                random.randint(4, 9)    # Durabilidad
            )
        elif part_type == PartType.TRANSMISSION:
            return (
                random.randint(4, 9),   # Velocidad de cambio
                random.randint(5, 10),  # Eficiencia de transmisión
                random.randint(3, 8)    # Control
            )
        else:  # WHEELS
            return (
                random.randint(3, 8),   # Tracción
                random.randint(4, 9),   # Manejo
                random.randint(5, 10)   # Agarre
            )

    async def _generate_part_image(self, part_type: PartType, config: CarConfig) -> bytes:
        """Genera la imagen para una parte específica del carro."""
        prompts = {
            PartType.ENGINE: f"detailed {config.engineType} car engine, {config.style} style",
            PartType.TRANSMISSION: f"detailed {config.transmissionType} car transmission, {config.style} style",
            PartType.WHEELS: f"detailed {config.wheelsType} car wheels, {config.style} style"
        }
        
        image_bytes = await self.stability_service.generate_car_variation(
            self._get_random_base_image(),
            prompts[part_type]
        )
        
        # Remover fondo
        img = Image.open(BytesIO(image_bytes))
        if self.rembg_session is None:
            self.rembg_session = new_session()
        output = remove(img, session=self.rembg_session)
        
        # Convertir a bytes
        img_byte_arr = BytesIO()
        output.save(img_byte_arr, format='PNG', optimize=True)
        return img_byte_arr.getvalue()

    async def generate_car_assets(self, config: CarConfig) -> dict:
        """Genera todos los assets del carro y sus estadísticas."""
        try:
            # 1. Generar imágenes de las partes
            images = {}
            parts_data = []
            
            # Generar imagen principal del carro
            car_image = await self.stability_service.generate_car_variation(
                self._get_random_base_image(),
                config.basePrompt
            )
            images['car'] = car_image
            
            # Generar imágenes de las partes
            for part_type in PartType:
                part_image = await self._generate_part_image(part_type, config)
                images[part_type.name.lower()] = part_image
                
                # Calcular stats para la parte
                stat1, stat2, stat3 = self._calculate_part_stats(part_type, config)
                
                parts_data.append({
                    'partType': part_type.value,
                    'stat1': stat1,
                    'stat2': stat2,
                    'stat3': stat3
                })
            
            # 2. Subir imágenes a Lighthouse
            uris = await self.lighthouse_service.upload_multiple_images(images)
            
            # 3. Construir respuesta final
            response = {
                'carImageURI': uris['carURI'],
                'parts': []
            }
            
            # Agregar URIs a las partes
            for part_data, part_type in zip(parts_data, PartType):
                part_data['imageURI'] = uris[f"{part_type.name.lower()}URI"]
                response['parts'].append(CarPart(**part_data))
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating car assets: {repr(e)}")
            raise Exception(f"Failed to generate car assets: {str(e)}")
