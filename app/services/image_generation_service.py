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
import asyncio
from typing import Dict, List, Tuple

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
        self.base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
        
        # Cargar imágenes de referencia por tipo
        self.reference_images = {
            'car': self._load_references('*.png'),
            'motor': self._load_references('motor/*.webp'),
            'transmission': self._load_references('transmission/*.webp'),
            'wheels': self._load_references('wheels/*.webp')
        }
        
        logger.info(f"Imágenes de referencia encontradas:")
        for key, images in self.reference_images.items():
            logger.info(f"- {key}: {len(images)} imágenes")

    def _load_references(self, pattern: str) -> List[str]:
        """Cargar imágenes de referencia según un patrón."""
        path = os.path.join(self.base_dir, pattern)
        images = glob.glob(path)
        if not images:
            logger.warning(f"No se encontraron imágenes para el patrón: {pattern}")
        return images

    def _get_random_reference(self, part_type: str) -> str:
        """Obtener una imagen de referencia aleatoria según el tipo."""
        images = self.reference_images.get(part_type, [])
        if not images:
            logger.warning(f"No hay imágenes de referencia para {part_type}, usando imágenes de carro")
            images = self.reference_images['car']
        
        selected = random.choice(images)
        logger.info(f"Usando imagen de referencia para {part_type}: {os.path.basename(selected)}")
        return selected

    async def _generate_and_upload(self, 
        part_type: str, 
        prompt: str, 
        reference_type: str
    ) -> Tuple[bytes, str]:
        """Generar y subir una imagen."""
        try:
            # Generar imagen
            image_bytes = await self.stability_service.generate_car_variation(
                self._get_random_reference(reference_type),
                prompt
            )
            
            # Remover fondo
            img = Image.open(BytesIO(image_bytes))
            if self.rembg_session is None:
                self.rembg_session = new_session()
            output = remove(img, session=self.rembg_session)
            
            # Convertir a bytes
            img_byte_arr = BytesIO()
            output.save(img_byte_arr, format='PNG', optimize=True)
            processed_bytes = img_byte_arr.getvalue()
            
            # Subir a Lighthouse
            uri = await self.lighthouse_service.upload_image(
                processed_bytes,
                f"{part_type}.png"
            )
            
            return processed_bytes, uri
        except Exception as e:
            logger.error(f"Error generando {part_type}: {str(e)}")
            raise

    async def generate_car_assets(self, config: CarConfig) -> dict:
        """Genera todos los assets del carro y sus estadísticas."""
        try:
            # Preparar tareas de generación
            tasks = [
                # Carro principal
                self._generate_and_upload(
                    'car',
                    config.basePrompt,
                    'car'
                ),
                # Motor
                self._generate_and_upload(
                    'engine',
                    f"detailed {config.engineType} car engine, {config.style} style, white background",
                    'motor'
                ),
                # Transmisión
                self._generate_and_upload(
                    'transmission',
                    f"detailed {config.transmissionType} car transmission, {config.style} style, white background",
                    'transmission'
                ),
                # Ruedas
                self._generate_and_upload(
                    'wheels',
                    f"detailed {config.wheelsType} car wheels, {config.style} style, white background",
                    'wheels'
                )
            ]
            
            # Ejecutar todas las generaciones en paralelo
            logger.info("Iniciando generación paralela de imágenes...")
            results = await asyncio.gather(*tasks)
            logger.info("Generación de imágenes completada")
            
            # Extraer URIs
            _, car_uri = results[0]
            _, engine_uri = results[1]
            _, transmission_uri = results[2]
            _, wheels_uri = results[3]
            
            # Generar estadísticas
            parts_data = []
            
            # Motor
            stat1, stat2, stat3 = self._calculate_engine_stats(config)
            parts_data.append(CarPart(
                partType=PartType.ENGINE,
                stat1=stat1,
                stat2=stat2,
                stat3=stat3,
                imageURI=engine_uri
            ))
            
            # Transmisión
            stat1, stat2, stat3 = self._calculate_transmission_stats(config)
            parts_data.append(CarPart(
                partType=PartType.TRANSMISSION,
                stat1=stat1,
                stat2=stat2,
                stat3=stat3,
                imageURI=transmission_uri
            ))
            
            # Ruedas
            stat1, stat2, stat3 = self._calculate_wheels_stats(config)
            parts_data.append(CarPart(
                partType=PartType.WHEELS,
                stat1=stat1,
                stat2=stat2,
                stat3=stat3,
                imageURI=wheels_uri
            ))
            
            # Construir respuesta final
            return {
                'carImageURI': car_uri,
                'parts': parts_data
            }
            
        except Exception as e:
            logger.error(f"Error generating car assets: {repr(e)}")
            raise Exception(f"Failed to generate car assets: {str(e)}")

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
