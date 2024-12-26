import os
import requests
import logging
from io import BytesIO
from ..config import settings

logger = logging.getLogger(__name__)

class LighthouseService:
    def __init__(self):
        self.api_key = settings.LIGHTHOUSE_API_KEY
        self.upload_url = "https://node.lighthouse.storage/api/v0/add"
        
    async def upload_image(self, image_bytes: bytes, filename: str) -> str:
        """
        Sube una imagen a Lighthouse y retorna su URI.
        """
        try:
            # Crear archivo temporal en memoria
            files = {
                'file': (filename, image_bytes, 'image/png')
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                self.upload_url,
                files=files,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Error uploading to Lighthouse: {response.text}")
                
            result = response.json()
            
            # Construir URI de IPFS
            ipfs_uri = f"https://gateway.lighthouse.storage/ipfs/{result['Hash']}"
            logger.info(f"Image uploaded successfully: {ipfs_uri}")
            
            return ipfs_uri
            
        except Exception as e:
            logger.error(f"Error uploading to Lighthouse: {str(e)}")
            raise Exception(f"Failed to upload image: {str(e)}")
            
    async def upload_multiple_images(self, images_dict: dict) -> dict:
        """
        Sube múltiples imágenes y retorna sus URIs.
        """
        result = {}
        for key, image_data in images_dict.items():
            uri = await self.upload_image(
                image_data,
                f"{key}.png"
            )
            result[f"{key}URI"] = uri
        return result 