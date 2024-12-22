from openai import OpenAI
from ..config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_car_image(self, prompt: str):
        try:
            print(f"Generando imagen con prompt: {prompt}")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=f"Un sprite de carro en vista superior 2D, estilo pixel art, fondo blanco. {prompt}",
                n=1,
                size="1024x1024",
                quality="standard",
                response_format="url"
            )
            
            if not response.data or not response.data[0].url:
                raise Exception("No se recibió URL de imagen en la respuesta")
                
            url = response.data[0].url
            print(f"Imagen generada exitosamente: {url[:50]}...")
            return url
            
        except Exception as e:
            error_message = f"Error generando imagen: {str(e)}"
            print(f"Error detallado: {repr(e)}")
            raise Exception(error_message)
