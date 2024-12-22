import requests
from ..config import settings
from ..models.car_model import CarStyle
import json
import base64
from io import BytesIO
import os
from PIL import Image
import tempfile

class StabilityService:
    def __init__(self):
        self.api_key = settings.STABILITY_API_KEY
        self.api_host = "https://api.stability.ai/v2beta/stable-image/control/structure"
        self.style_prompts = {
            CarStyle.PIXEL_ART: "A sports car in top-down 2D view, pixel art style, vibrant colors, white background",
            CarStyle.REALISTIC: "A sports car in top-down 2D view, photorealistic style, modern and aerodynamic design, white background",
            CarStyle.CARTOON: "A sports car in top-down 2D view, modern cartoon style, clean design, white background",
            CarStyle.MINIMALIST: "A sports car in top-down 2D view, minimalist style, simple lines, elegant design, white background"
        }

    def _resize_image(self, image_path: str) -> str:
        """Redimensiona la imagen a 1024x1024 píxeles y guarda una copia temporal."""
        # Crear un archivo temporal con un nombre único
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_resized_{os.getpid()}.png")
        
        with Image.open(image_path) as img:
            # Redimensionar la imagen manteniendo la proporción
            img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
            # Guardar la imagen redimensionada en el archivo temporal
            img.save(temp_path, format='PNG')
        
        return temp_path

    def send_generation_request(self, params, files=None):
        """Envía la solicitud a la API de Stability siguiendo el formato del ejemplo."""
        headers = {
            "Accept": "image/*",
            "Authorization": f"Bearer {self.api_key}"
        }

        if files is None:
            files = {}

        file_handle = None
        try:
            # Codificar parámetros
            image = params.pop("image", None)
            if image is not None and image != '':
                file_handle = open(image, 'rb')
                files["image"] = file_handle
            if len(files) == 0:
                files["none"] = ''

            print(f"Sending request to Stability AI...")
            response = requests.post(
                self.api_host,
                headers=headers,
                files=files,
                data=params
            )
            
            if not response.ok:
                raise Exception(f"Error in Stability API: {response.text}")

            return response.content

        finally:
            # Cerrar el archivo si está abierto
            if file_handle is not None:
                file_handle.close()

    async def generate_car_variation(self, image_path: str, prompt: str, style: CarStyle = CarStyle.REALISTIC) -> bytes:
        temp_image_path = None
        try:
            if not os.path.exists(image_path):
                raise Exception(f"Image not found at: {image_path}")

            # Redimensionar la imagen y obtener la ruta temporal
            temp_image_path = self._resize_image(image_path)

            style_prompt = self.style_prompts[style]
            # Asumimos que el prompt del usuario está en español, lo dejamos como está
            # pero agregamos el estilo en inglés
            full_prompt = f"{style_prompt}. {prompt}"
            
            # Preparar los parámetros siguiendo el formato del ejemplo
            params = {
                "image": temp_image_path,
                "control_strength": "0.7",
                "prompt": full_prompt,
                "negative_prompt": "low quality, distorted, bad proportions, blurry, pixelated",
                "seed": "0",
                "steps": "30",
                "output_format": "png"
            }
            
            # No usar await aquí ya que send_generation_request no es una función asíncrona
            return self.send_generation_request(params)

        except Exception as e:
            error_message = f"Error generating car variation: {str(e)}"
            print(f"Detailed error: {repr(e)}")
            raise Exception(error_message)
            
        finally:
            # Limpiar el archivo temporal
            if temp_image_path and os.path.exists(temp_image_path):
                try:
                    os.remove(temp_image_path)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")