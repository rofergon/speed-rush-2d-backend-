from .openai_service import OpenAIService

class ImageGenerationService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def generate_car_sprite(self, prompt: str) -> str:
        try:
            # Generar imagen con OpenAI y devolver la URL
            image_url = await self.openai_service.generate_car_image(prompt)
            print(f"URL de imagen generada: {image_url}")
            return image_url
                
        except Exception as e:
            print(f"Error detallado: {repr(e)}")
            raise Exception(f"Error generando imagen: {str(e)}")
