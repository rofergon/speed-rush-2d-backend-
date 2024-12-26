import requests
import json
import time
from typing import Dict, List

def check_server_health(base_url):
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        return True
    except:
        return False

def test_generate_car(prompt: str, style: str = "cartoon", max_retries=5, retry_delay=10):
    # URL base y endpoint
    base_url = "https://speed-rush-2d-backend-production.up.railway.app"
    url = f"{base_url}/api/cars/generate"
    
    # Datos para la solicitud
    data = {
        "prompt": prompt,
        "style": style
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
            assert "carImageURI" in result, "La respuesta no contiene carImageURI"
            assert "parts" in result, "La respuesta no contiene parts"
            assert len(result["parts"]) == 3, "La respuesta debe contener 3 partes"
            
            # Imprimir la imagen principal del carro
            print(f"\n🚗 Imagen principal del carro:")
            print(f"URI: {result['carImageURI']}")
            
            # Imprimir información de cada parte
            print("\n🔧 Partes del carro:")
            part_types = ["ENGINE", "TRANSMISSION", "WHEELS"]
            
            for part, part_type in zip(result["parts"], part_types):
                print(f"\n{part_type}:")
                print(f"  URI: {part['imageURI']}")
                print(f"  Stats:")
                print(f"    - Stat1: {part['stat1']}/10")
                print(f"    - Stat2: {part['stat2']}/10")
                print(f"    - Stat3: {part['stat3']}/10")
                
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

def test_multiple_styles():
    """Prueba la generación de carros en diferentes estilos."""
    styles = ["pixel_art", "realistic", "cartoon", "minimalist"]
    prompts = [
        "a high-performance sports car with aerodynamic design",
        "a futuristic racing car with advanced technology",
        "a classic muscle car with powerful engine",
        "a sleek modern supercar with elegant lines"
    ]
    
    results = []
    for style, prompt in zip(styles, prompts):
        print(f"\n🚗 Generando carro en estilo {style}...")
        success, message = test_generate_car(prompt, style)
        results.append({
            "style": style,
            "success": success,
            "message": message
        })
        time.sleep(5)  # Esperar entre generaciones
    
    return results

if __name__ == "__main__":
    print("Iniciando tests de generación de carros...")
    results = test_multiple_styles()
    
    print("\n📊 Resultados finales:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['style']}: {result['message']}") 