from .openai_service import OpenAIService
import requests
from io import BytesIO
from rembg import remove, new_session
from PIL import Image
import base64

class ImageGenerationService:
    def __init__(self):
        self.openai_service = OpenAIService()
        # Inicializar la sesión de rembg una sola vez
        self.rembg_session = new_session()

    async def generate_car_sprite(self, prompt: str) -> str:
        try:
            # Generar imagen con OpenAI y obtener la URL
            image_url = await self.openai_service.generate_car_image(prompt)
            print(f"URL de imagen generada: {image_url}")
            
            try:
                # Descargar la imagen con timeout
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()  # Verificar si hay errores HTTP
                
                # Abrir y verificar la imagen
                img = Image.open(BytesIO(response.content))
                
                # Remover el fondo usando la sesión pre-cargada
                output = remove(img, session=self.rembg_session)
                
                # Optimizar la imagen antes de convertirla
                output = output.convert('RGBA')
                
                # Convertir la imagen procesada a base64
                buffered = BytesIO()
                output.save(buffered, format="PNG", optimize=True)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return f"data:image/png;base64,{img_str}"
                
            except requests.exceptions.RequestException as e:
                print(f"Error descargando la imagen: {e}")
                raise Exception("Error al descargar la imagen generada")
            except Exception as e:
                print(f"Error procesando la imagen: {e}")
                raise Exception("Error al procesar la imagen")
                
        except Exception as e:
            print(f"Error detallado: {repr(e)}")
            raise Exception(f"Error generando imagen: {str(e)}")
