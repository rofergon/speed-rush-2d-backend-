from openai import OpenAI
from ..config import settings
from ..models.car_model import CarStyle

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.style_prompts = {
            CarStyle.PIXEL_ART: "Un sprite de carro en vista superior 2D, estilo pixel art, fondo blanco.",
            CarStyle.REALISTIC: "Un carro en vista superior 2D, estilo fotorrealista, fondo blanco, alta calidad.",
            CarStyle.CARTOON: "Un carro en vista superior 2D, estilo caricatura moderna, fondo blanco, diseño limpio.",
            CarStyle.MINIMALIST: "Un carro en vista superior 2D, estilo minimalista y moderno, fondo blanco, líneas simples."
        }

    async def generate_car_image(self, prompt: str, style: CarStyle = CarStyle.REALISTIC):
        try:
            style_prompt = self.style_prompts[style]
            full_prompt = f"{style_prompt} {prompt}"
            print(f"Generando imagen con prompt: {full_prompt}")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
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
