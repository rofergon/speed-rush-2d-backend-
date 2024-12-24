import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os
import time

def check_server_health(base_url):
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        return True
    except:
        return False

def test_generate_car(max_retries=5, retry_delay=10):
    # URL base y endpoint
    base_url = "https://speed-rush-2d-backend-production.up.railway.app"
    url = f"{base_url}/api/cars/generate"
    
    # Datos para la solicitud
    data = {
        "prompt": "un carro deportivo rojo con diseño futurista",
        "style": "cartoon"
    }
    
    # Verificar salud del servidor
    print("Verificando estado del servidor...")
    if not check_server_health(base_url):
        print("⚠️ El servidor no está respondiendo, esperando...")
        time.sleep(retry_delay)
    
    # Intentar la generación con reintentos
    for attempt in range(max_retries):
        try:
            print(f"\nIntento {attempt + 1} de {max_retries}")
            
            # Realizar la solicitud POST con timeout más largo
            print("Enviando solicitud para generar carro...")
            response = requests.post(url, json=data, timeout=60)
            
            # Verificar si la solicitud fue exitosa
            response.raise_for_status()
            
            # Obtener la respuesta como JSON
            result = response.json()
            
            # Verificar la estructura de la respuesta
            assert "image" in result, "La respuesta no contiene el campo 'image'"
            assert "metadata" in result, "La respuesta no contiene el campo 'metadata'"
            assert "traits" in result["metadata"], "La respuesta no contiene traits"
            
            # Decodificar y guardar la imagen
            image_data = base64.b64decode(result["image"]["data"])
            image = Image.open(BytesIO(image_data))
            
            # Crear directorio para las imágenes si no existe
            os.makedirs("generated_cars", exist_ok=True)
            
            # Guardar la imagen
            image_path = f"generated_cars/test_car_{int(time.time())}.png"
            image.save(image_path)
            print(f"Imagen guardada en: {image_path}")
            
            # Imprimir los traits del carro
            print("\nTraits del carro generado:")
            for trait, value in result["metadata"]["traits"].items():
                print(f"{trait}: {value}")
                
            return True, "Test completado exitosamente"
            
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud HTTP: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                return False, f"Error en la solicitud HTTP después de {max_retries} intentos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

if __name__ == "__main__":
    print("Iniciando test de generación de carro...")
    success, message = test_generate_car()
    
    if success:
        print("\n✅ Test exitoso!")
        print(message)
    else:
        print("\n❌ Test fallido!")
        print(message) 