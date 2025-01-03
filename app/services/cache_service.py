import json
import os
import time
import logging
from typing import Optional, Dict, List
from ..models.car_model import CarPart, PartType

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # Obtener la ruta absoluta del directorio raíz del proyecto
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.cache_dir = os.path.join(project_root, "cache")
        logger.info(f"Directorio de caché configurado en: {self.cache_dir}")
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Asegura que el directorio de caché exista."""
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
                logger.info(f"Directorio de caché creado en: {self.cache_dir}")
            else:
                logger.info(f"Usando directorio de caché existente: {self.cache_dir}")
                # Listar archivos existentes
                cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
                logger.info(f"Archivos en caché encontrados: {len(cache_files)}")
                for file in cache_files:
                    logger.debug(f"Archivo en caché: {file}")
        except Exception as e:
            logger.error(f"Error creando directorio de caché: {str(e)}")
            raise
    
    def _convert_part_to_dict(self, part: CarPart) -> Dict:
        """Convierte un objeto CarPart a diccionario."""
        return {
            "partType": str(part.partType),
            "stat1": part.stat1,
            "stat2": part.stat2,
            "stat3": part.stat3,
            "imageURI": part.imageURI
        }
    
    def save_response(self, response_data: Dict) -> str:
        """Guarda una respuesta pre-generada y retorna su ID."""
        try:
            # Convertir la respuesta a un formato serializable
            serializable_response = {
                "carImageURI": response_data["carImageURI"],
                "parts": [self._convert_part_to_dict(part) for part in response_data["parts"]]
            }
            
            # Generar un ID único basado en el timestamp
            cache_id = str(int(time.time() * 1000))
            
            # Crear archivo de caché
            cache_file = os.path.join(self.cache_dir, f"{cache_id}.json")
            logger.info(f"Guardando respuesta en: {cache_file}")
            
            # Guardar con formato pretty para mejor legibilidad
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_response, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Respuesta guardada en caché con ID: {cache_id}")
            logger.debug(f"Contenido guardado: {json.dumps(serializable_response, indent=2)}")
            return cache_id
            
        except Exception as e:
            logger.error(f"Error guardando respuesta en caché: {str(e)}")
            raise
    
    def get_cached_response(self) -> Optional[Dict]:
        """Obtiene y elimina una respuesta pre-generada si está disponible."""
        try:
            # Buscar archivos de caché disponibles
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            
            if not cache_files:
                logger.info("No hay respuestas pre-generadas disponibles")
                return None
                
            # Tomar el primer archivo disponible
            cache_file = os.path.join(self.cache_dir, cache_files[0])
            logger.info(f"Intentando leer archivo de caché: {cache_file}")
            
            try:
                # Leer la respuesta
                with open(cache_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.debug(f"Contenido leído del caché: {content}")
                    response_data = json.loads(content)
                
                # Eliminar el archivo usado
                os.remove(cache_file)
                logger.info(f"Respuesta de caché utilizada y eliminada: {cache_files[0]}")
                
                return response_data
                
            except json.JSONDecodeError as je:
                logger.error(f"Error decodificando JSON del caché: {str(je)}")
                # Si hay error en el JSON, eliminar el archivo corrupto
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    logger.info(f"Archivo de caché corrupto eliminado: {cache_file}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo respuesta de caché: {str(e)}")
            return None 