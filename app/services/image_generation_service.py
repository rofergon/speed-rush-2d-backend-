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
from openai import OpenAI
from ..config import settings

logger = logging.getLogger(__name__)

class ImageGenerationService:
    def __init__(self):
        self.stability_service = StabilityService()
        self.lighthouse_service = LighthouseService()
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
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
            'motor': self._load_references('motor/*.{png,jpg,jpeg,webp}'),
            'transmission': self._load_references('transmission/*.{png,jpg,jpeg,webp}'),
            'wheels': self._load_references('wheels/*.{png,jpg,jpeg,webp}')
        }
        
        logger.info(f"Imágenes de referencia encontradas:")
        for key, images in self.reference_images.items():
            logger.info(f"- {key}: {len(images)} imágenes")

    def _load_references(self, pattern: str) -> List[str]:
        """Cargar imágenes de referencia según un patrón."""
        path = os.path.join(self.base_dir, pattern)
        # Usar glob.glob con múltiples patrones
        if '{' in pattern:
            # Si el patrón tiene llaves, expandir para cada extensión
            images = []
            for ext in ['png', 'jpg', 'jpeg', 'webp']:
                expanded_path = path.replace('{png,jpg,jpeg,webp}', ext)
                images.extend(glob.glob(expanded_path))
        else:
            # Si es un patrón simple, usarlo directamente
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

    async def _generate_creative_prompt(self) -> tuple[str, str]:
        """Genera un prompt creativo para el carro usando generación local."""
        try:
            # Listas de elementos para generar descripciones
            colors = ["rojo", "azul", "verde", "negro", "blanco", "amarillo", "plateado", "dorado", "naranja", "púrpura"]
            styles = ["futurista", "clásico", "moderno", "retro", "elegante", "agresivo", "deportivo", "luxury"]
            details = ["con detalles cromados", "con líneas aerodinámicas", "con alerones deportivos", "con diseño minimalista"]
            features = [
                "con faros LED integrados",
                "con tomas de aire laterales",
                "con parrilla frontal distintiva",
                "con perfil bajo y estilizado",
                "con curvas suaves y elegantes",
                "con diseño angular y agresivo",
                "con acabados metálicos premium",
                "con líneas deportivas fluidas"
            ]
            
            # Generar descripción aleatoria más detallada
            selected_color = random.choice(colors)
            selected_style = random.choice(styles)
            selected_details = random.choice(details)
            selected_features = random.choice(features)
            
            creative_prompt = f"carro {selected_style} {selected_color} {selected_details} {selected_features}"
            
            # Mapear colores a inglés para las partes
            color_mapping = {
                "rojo": "red colored, crimson accents",
                "azul": "blue colored, metallic blue accents",
                "verde": "green colored, emerald accents",
                "negro": "black colored, dark chrome accents",
                "blanco": "white colored, pearl accents",
                "amarillo": "yellow colored, gold accents",
                "plateado": "silver colored, chrome accents",
                "dorado": "gold colored, bronze accents",
                "naranja": "orange colored, copper accents",
                "púrpura": "purple colored, metallic accents"
            }
            
            color_base = color_mapping.get(selected_color, "metallic colored, chrome accents")
            
            logger.info(f"Prompt generado: {creative_prompt}")
            return creative_prompt, color_base
            
        except Exception as e:
            logger.error(f"Error generando prompt creativo: {str(e)}")
            return "modern sports car with aerodynamic design", "metallic colored, chrome accents"

    async def generate_car_assets(self, config: CarConfig) -> dict:
        """Genera todos los assets del carro y sus estadísticas."""
        try:
            logger.info("Iniciando generación paralela de imágenes...")
            
            # Generar prompt creativo
            creative_prompt, base_colors = await self._generate_creative_prompt()
            
            # Preparar todas las referencias y prompts primero
            car_ref = self._get_random_reference('car')
            engine_ref = self._get_random_reference('motor')
            transmission_ref = self._get_random_reference('transmission')
            wheels_ref = self._get_random_reference('wheels')
            
            # Crear todas las tareas de generación al mismo tiempo
            tasks = []
            
            # Carro principal - usar el prompt creativo
            car_prompt = f"{creative_prompt}, perfect top-down view, centered, high quality, detailed design"
            tasks.append(self.stability_service.generate_car_variation(
                car_ref,
                car_prompt,
                config.style
            ))
            
            # Motor - prompt específico para motor
            engine_prompt = f"detailed {config.engineType} car engine, {base_colors}, technical diagram style, mechanical parts visible, pistons, cylinders, valves, highly detailed engine block, {config.style} style, centered on pure white background"
            tasks.append(self.stability_service.generate_car_variation(
                engine_ref,
                engine_prompt,
                config.style
            ))
            
            # Transmisión - prompt específico para transmisión
            transmission_prompt = f"detailed automotive {config.transmissionType} transmission gearbox mechanism, {base_colors}, technical diagram style, car transmission parts visible, automotive gearbox, mechanical transmission system, drivetrain components, vehicle transmission, {config.style} style, centered on pure white background"
            tasks.append(self.stability_service.generate_car_variation(
                transmission_ref,
                transmission_prompt,
                config.style
            ))
            
            # Ruedas - prompt específico para ruedas
            wheels_prompt = f"detailed automotive {config.wheelsType} car wheel and tire assembly, {base_colors}, automotive wheel design, car rim details, vehicle tire tread pattern, automotive brake system, car wheel components, vehicle wheel, {config.style} style, centered on pure white background"
            tasks.append(self.stability_service.generate_car_variation(
                wheels_ref,
                wheels_prompt,
                config.style
            ))
            
            # Ejecutar todas las generaciones en paralelo
            logger.info("Ejecutando generación de imágenes en paralelo...")
            logger.info(f"Prompts utilizados:")
            logger.info(f"Carro: {car_prompt}")
            logger.info(f"Motor: {engine_prompt}")
            logger.info(f"Transmisión: {transmission_prompt}")
            logger.info(f"Ruedas: {wheels_prompt}")
            
            image_results = await asyncio.gather(*tasks)
            logger.info("Generación de imágenes completada")
            
            # Procesar y subir las imágenes generadas
            upload_tasks = []
            for idx, (part_type, image_bytes) in enumerate([
                ('car', image_results[0]),
                ('engine', image_results[1]),
                ('transmission', image_results[2]),
                ('wheels', image_results[3])
            ]):
                # Remover fondo
                img = Image.open(BytesIO(image_bytes))
                if self.rembg_session is None:
                    self.rembg_session = new_session()
                output = remove(img, session=self.rembg_session)
                
                # Convertir a bytes
                img_byte_arr = BytesIO()
                output.save(img_byte_arr, format='PNG', optimize=True)
                processed_bytes = img_byte_arr.getvalue()
                
                # Agregar tarea de subida
                upload_tasks.append(self.lighthouse_service.upload_image(
                    processed_bytes,
                    f"{part_type}.png"
                ))
            
            # Subir todas las imágenes en paralelo
            logger.info("Subiendo imágenes en paralelo...")
            uris = await asyncio.gather(*upload_tasks)
            logger.info("Subida de imágenes completada")
            
            # Extraer URIs
            car_uri = uris[0]
            engine_uri = uris[1]
            transmission_uri = uris[2]
            wheels_uri = uris[3]
            
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

    def _generate_weighted_stat(self) -> int:
        """
        Genera un número entre 1 y 10 donde 9 y 10 tienen 30% menos probabilidad
        """
        numbers = list(range(1, 11))
        # Los números 1-8 tienen peso 1.0, mientras que 9 y 10 tienen peso 0.7
        weights = [1.0] * 8 + [0.7] * 2
        return random.choices(numbers, weights=weights)[0]

    def _calculate_engine_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calculate engine statistics based on configuration."""
        return (
            self._generate_weighted_stat(),  # Potencia
            self._generate_weighted_stat(),  # Eficiencia
            self._generate_weighted_stat()   # Durabilidad
        )

    def _calculate_transmission_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calculate transmission statistics based on configuration."""
        return (
            self._generate_weighted_stat(),  # Velocidad de cambio
            self._generate_weighted_stat(),  # Eficiencia
            self._generate_weighted_stat()   # Control
        )

    def _calculate_wheels_stats(self, config: CarConfig) -> tuple[int, int, int]:
        """Calculate wheels statistics based on configuration."""
        return (
            self._generate_weighted_stat(),  # Tracción
            self._generate_weighted_stat(),  # Manejo
            self._generate_weighted_stat()   # Agarre
        )
