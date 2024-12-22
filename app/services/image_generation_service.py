from .stability_service import StabilityService
import requests
from io import BytesIO
from rembg import remove, new_session
from PIL import Image
import os

class ImageGenerationService:
    def __init__(self):
        self.stability_service = StabilityService()
        # Inicializar la sesión de rembg una sola vez
        self.rembg_session = new_session()
        # Ruta base para las imágenes
        self.base_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "car1-enhanced.png")

    async def generate_car_sprite(self, prompt: str) -> bytes:
        try:
            # Generar variación del carro base usando Stability AI
            image_bytes = await self.stability_service.generate_car_variation(self.base_image_path, prompt)
            print("Variación del carro generada con Stability AI")
            
            try:
                # Abrir y verificar la imagen
                img = Image.open(BytesIO(image_bytes))
                
                # Remover el fondo usando la sesión pre-cargada
                output = remove(img, session=self.rembg_session)
                
                # Optimizar la imagen antes de convertirla
                output = output.convert('RGBA')
                
                # Convertir la imagen a bytes
                img_byte_arr = BytesIO()
                output.save(img_byte_arr, format='PNG', optimize=True)
                return img_byte_arr.getvalue()
                
            except Exception as e:
                print(f"Error procesando la imagen: {e}")
                raise Exception("Error al procesar la imagen")
                
        except Exception as e:
            print(f"Error detallado: {repr(e)}")
            raise Exception(f"Error generando imagen: {str(e)}")
