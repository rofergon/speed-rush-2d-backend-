from .stability_service import StabilityService
import requests
from io import BytesIO
from rembg import remove, new_session
from PIL import Image
import os
import random
from ..models.car_model import CarTraits

class ImageGenerationService:
    def __init__(self):
        self.stability_service = StabilityService()
        self.rembg_session = new_session()
        self.base_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "car1-enhanced.png")
        
        # Listas de elementos para generar prompts más detallados
        self.colors = [
            "metallic red", "pearl white", "electric blue", "racing yellow", 
            "midnight black", "british racing green", "candy orange",
            "chrome silver", "matte black", "neon purple", "carbon black",
            "ferrari red", "lamborghini yellow", "porsche silver"
        ]
        
        self.car_brands = [
            "Ferrari", "Lamborghini", "Porsche", "McLaren", "Bugatti",
            "Aston Martin", "Koenigsegg", "Pagani", "Maserati", "BMW M",
            "Mercedes-AMG", "Audi Sport"
        ]
        
        self.car_features = [
            "carbon fiber hood", "wide body kit", "rear spoiler",
            "side skirts", "LED headlights", "custom rims",
            "dual exhaust", "tinted windows", "hood scoop",
            "diffuser", "front splitter", "air intakes"
        ]
        
        # Diccionario de variaciones de prompts por estilo
        self.style_variations = {
            'PIXEL_ART': [
                "inspired by OutRun arcade game, {color}, {feature}",
                "retro racing game style, {brand} inspired, {color} with neon accents",
                "8-bit racing classic, {color}, {feature}, synthwave style",
                "pixel perfect {brand} racer, {color}, {feature}",
                "classic arcade racer, {color} with {feature}, retro gaming vibes"
            ],
            'REALISTIC': [
                "hyperrealistic {brand} supercar, {color}, with {feature}",
                "photorealistic {color} sports car, {brand} inspired design, {feature}",
                "ultra-detailed {brand} style racer, {color}, featuring {feature}",
                "professional racing car, {color} {brand} design, with {feature}",
                "{brand} track car, {color} finish, aggressive {feature}"
            ],
            'CARTOON': [
                "animated {brand} style racer, {color}, fun {feature}",
                "playful {color} sports car, {brand} inspired, with exaggerated {feature}",
                "cartoon {brand} supercar, {color}, stylized {feature}",
                "whimsical racing car, {color} {brand} design, with cute {feature}",
                "animated movie style {brand}, {color}, with dynamic {feature}"
            ],
            'MINIMALIST': [
                "clean {brand} design, {color}, subtle {feature}",
                "elegant {color} sports car, {brand} inspired lines, minimal {feature}",
                "simplified {brand} silhouette, {color}, essential {feature}",
                "pure {color} design, {brand} DNA, refined {feature}",
                "geometric {brand} interpretation, {color}, with streamlined {feature}"
            ]
        }

    def _generate_random_traits(self) -> CarTraits:
        """Genera traits aleatorios para el carro."""
        return CarTraits(
            speed=random.randint(1, 10),
            acceleration=random.randint(1, 10),
            handling=random.randint(1, 10),
            drift_factor=random.randint(1, 10),
            turn_factor=random.randint(1, 10),
            max_speed=random.randint(1, 10)
        )

    def _get_random_elements(self):
        """Obtiene elementos aleatorios para construir el prompt."""
        return {
            'color': random.choice(self.colors),
            'brand': random.choice(self.car_brands),
            'feature': random.choice(self.car_features)
        }

    def _get_random_variation(self, style: str) -> str:
        """Obtiene una variación aleatoria del prompt para un estilo específico."""
        variations = self.style_variations.get(style, [])
        if variations:
            template = random.choice(variations)
            elements = self._get_random_elements()
            return template.format(**elements)
        return ""

    async def generate_car_sprite(self, prompt: str) -> tuple[bytes, CarTraits]:
        try:
            # Determinar el estilo basado en el prompt o usar uno aleatorio
            style = None
            for style_name in self.style_variations.keys():
                if style_name.lower() in prompt.lower():
                    style = style_name
                    break
            
            if not style:
                style = random.choice(list(self.style_variations.keys()))
            
            # Obtener una variación aleatoria para el estilo
            variation = self._get_random_variation(style)
            
            # Combinar el prompt original con la variación
            enhanced_prompt = f"{prompt}. {variation}"
            print(f"Generating car with enhanced prompt: {enhanced_prompt}")
            
            # Generar variación del carro base usando Stability AI
            image_bytes = await self.stability_service.generate_car_variation(self.base_image_path, enhanced_prompt)
            print("Car variation generated with Stability AI")
            
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
                
                # Generar traits aleatorios
                traits = self._generate_random_traits()
                
                return img_byte_arr.getvalue(), traits
                
            except Exception as e:
                print(f"Error processing image: {e}")
                raise Exception("Error processing the image")
                
        except Exception as e:
            print(f"Detailed error: {repr(e)}")
            raise Exception(f"Error generating image: {str(e)}")
