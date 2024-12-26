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

    def _calculate_engine_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calcula las estadísticas del motor."""
        if config.engineType == "performance":
            return (
                random.randint(7, 10),  # Potencia
                random.randint(5, 8),   # Eficiencia
                random.randint(6, 9)    # Durabilidad
            )
        elif config.engineType == "eco":
            return (
                random.randint(4, 7),   # Potencia
                random.randint(7, 10),  # Eficiencia
                random.randint(7, 10)   # Durabilidad
            )
        else:  # standard
            return (
                random.randint(5, 8),   # Potencia
                random.randint(5, 8),   # Eficiencia
                random.randint(5, 8)    # Durabilidad
            )

    def _calculate_transmission_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calcula las estadísticas de la transmisión."""
        if config.transmissionType == "automatic":
            return (
                random.randint(6, 9),   # Velocidad de cambio
                random.randint(7, 10),  # Eficiencia
                random.randint(5, 8)    # Control
            )
        elif config.transmissionType == "manual":
            return (
                random.randint(7, 10),  # Velocidad de cambio
                random.randint(5, 8),   # Eficiencia
                random.randint(7, 10)   # Control
            )
        else:  # sequential
            return (
                random.randint(8, 10),  # Velocidad de cambio
                random.randint(6, 9),   # Eficiencia
                random.randint(6, 9)    # Control
            )

    def _calculate_wheels_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calcula las estadísticas de las ruedas."""
        if config.wheelsType == "racing":
            return (
                random.randint(7, 10),  # Tracción
                random.randint(7, 10),  # Manejo
                random.randint(6, 9)    # Agarre
            )
        elif config.wheelsType == "offroad":
            return (
                random.randint(8, 10),  # Tracción
                random.randint(5, 8),   # Manejo
                random.randint(7, 10)   # Agarre
            )
        else:  # standard
            return (
                random.randint(5, 8),   # Tracción
                random.randint(5, 8),   # Manejo
                random.randint(5, 8)    # Agarre
            )

    async def _generate_part_image(self, part_type: PartType, config: CarConfig) -> bytes:
        """Genera la imagen para una parte específica del carro."""
        prompts = {
            PartType.ENGINE: f"detailed {config.engineType} car engine, {config.style} style, white background",
            PartType.TRANSMISSION: f"detailed {config.transmissionType} car transmission, {config.style} style, white background",
            PartType.WHEELS: f"detailed {config.wheelsType} car wheels, {config.style} style, white background"
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
            
            # Subir imagen principal a Lighthouse
            car_uri = await self.lighthouse_service.upload_image(car_image, "car.png")
            
            # Generar y subir imágenes de las partes
            for part_type in PartType:
                # Generar imagen de la parte
                part_image = await self._generate_part_image(part_type, config)
                
                # Subir imagen a Lighthouse
                part_uri = await self.lighthouse_service.upload_image(
                    part_image,
                    f"{part_type.name.lower()}.png"
                )
                
                # Calcular estadísticas según el tipo de parte
                if part_type == PartType.ENGINE:
                    stat1, stat2, stat3 = self._calculate_engine_stats(config)
                elif part_type == PartType.TRANSMISSION:
                    stat1, stat2, stat3 = self._calculate_transmission_stats(config)
                else:  # WHEELS
                    stat1, stat2, stat3 = self._calculate_wheels_stats(config)
                
                # Agregar datos de la parte
                parts_data.append(CarPart(
                    partType=part_type,
                    stat1=stat1,
                    stat2=stat2,
                    stat3=stat3,
                    imageURI=part_uri
                ))
            
            # Construir respuesta final
            return {
                'carImageURI': car_uri,
                'parts': parts_data
            }
            
        except Exception as e:
            logger.error(f"Error generating car assets: {repr(e)}")
            raise Exception(f"Failed to generate car assets: {str(e)}")
